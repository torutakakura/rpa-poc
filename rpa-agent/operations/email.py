"""
K_メール カテゴリの操作
"""

import email
import imaplib
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class EmailSendOperation(BaseOperation):
    """メール送信"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        smtp_server = params.get("smtp_server", "smtp.gmail.com")
        smtp_port = params.get("smtp_port", 587)
        username = params.get("username", "")
        password = params.get("password", "")
        from_email = params.get("from_email", "")
        to_emails = params.get("to_emails", [])
        cc_emails = params.get("cc_emails", [])
        bcc_emails = params.get("bcc_emails", [])
        subject = params.get("subject", "")
        body = params.get("body", "")
        body_type = params.get("body_type", "plain")  # plain or html
        attachments = params.get("attachments", [])

        error = self.validate_params(
            params, ["username", "password", "to_emails", "subject"]
        )
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # メッセージの作成
            msg = MIMEMultipart()
            msg["From"] = from_email or username
            msg["To"] = (
                ", ".join(to_emails) if isinstance(to_emails, list) else to_emails
            )
            if cc_emails:
                msg["Cc"] = (
                    ", ".join(cc_emails) if isinstance(cc_emails, list) else cc_emails
                )
            msg["Subject"] = subject

            # 本文の追加
            msg.attach(MIMEText(body, body_type))

            # 添付ファイルの追加
            for attachment_path in attachments:
                if os.path.exists(attachment_path):
                    with open(attachment_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(attachment_path)}",
                        )
                        msg.attach(part)

            # SMTPサーバーに接続して送信
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)

                # 全ての受信者リストを作成
                all_recipients = to_emails
                if cc_emails:
                    all_recipients.extend(cc_emails)
                if bcc_emails:
                    all_recipients.extend(bcc_emails)

                server.send_message(msg, to_addrs=all_recipients)

            self.log(f"Email sent successfully to {to_emails}")

            return OperationResult(
                status="success",
                data={
                    "to": to_emails,
                    "subject": subject,
                    "attachments_count": len(attachments),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to send email: {str(e)}"
            )


class EmailReceiveOperation(BaseOperation):
    """メール受信"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        imap_server = params.get("imap_server", "imap.gmail.com")
        imap_port = params.get("imap_port", 993)
        username = params.get("username", "")
        password = params.get("password", "")
        folder = params.get("folder", "INBOX")
        search_criteria = params.get("search_criteria", "ALL")
        max_emails = params.get("max_emails", 10)
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["username", "password"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # IMAPサーバーに接続
            with imaplib.IMAP4_SSL(imap_server, imap_port) as mail:
                mail.login(username, password)
                mail.select(folder)

                # メールを検索
                status, messages = mail.search(None, search_criteria)
                if status != "OK":
                    return OperationResult(
                        status="failure", data={}, error="Failed to search emails"
                    )

                # メールIDリストを取得
                email_ids = messages[0].split()
                email_ids = (
                    email_ids[-max_emails:]
                    if len(email_ids) > max_emails
                    else email_ids
                )

                emails = []
                for email_id in email_ids:
                    # メールを取得
                    status, msg_data = mail.fetch(email_id, "(RFC822)")
                    if status != "OK":
                        continue

                    # メールをパース
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # メール情報を抽出
                    email_info = {
                        "id": email_id.decode(),
                        "from": msg.get("From"),
                        "to": msg.get("To"),
                        "subject": msg.get("Subject"),
                        "date": msg.get("Date"),
                        "body": self._get_email_body(msg),
                    }
                    emails.append(email_info)

                # ストレージに保存
                if storage_key:
                    self.set_storage(storage_key, emails)
                    self.log(f"Stored {len(emails)} emails as '{storage_key}'")

            self.log(f"Received {len(emails)} emails from {folder}")

            return OperationResult(
                status="success",
                data={"emails": emails, "count": len(emails), "folder": folder},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to receive emails: {str(e)}"
            )

    def _get_email_body(self, msg):
        """メール本文を抽出"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body = part.get_payload(decode=True).decode(
                        "utf-8", errors="ignore"
                    )
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        return body


class EmailDeleteOperation(BaseOperation):
    """メール削除"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        imap_server = params.get("imap_server", "imap.gmail.com")
        imap_port = params.get("imap_port", 993)
        username = params.get("username", "")
        password = params.get("password", "")
        folder = params.get("folder", "INBOX")
        email_ids = params.get("email_ids", [])

        error = self.validate_params(params, ["username", "password", "email_ids"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # IMAPサーバーに接続
            with imaplib.IMAP4_SSL(imap_server, imap_port) as mail:
                mail.login(username, password)
                mail.select(folder)

                deleted_count = 0
                for email_id in email_ids:
                    # メールに削除フラグを設定
                    mail.store(str(email_id), "+FLAGS", "\\Deleted")
                    deleted_count += 1

                # 削除を確定
                mail.expunge()

            self.log(f"Deleted {deleted_count} emails")

            return OperationResult(
                status="success",
                data={"deleted_count": deleted_count, "folder": folder},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to delete emails: {str(e)}"
            )


class EmailMoveOperation(BaseOperation):
    """メール移動"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        imap_server = params.get("imap_server", "imap.gmail.com")
        imap_port = params.get("imap_port", 993)
        username = params.get("username", "")
        password = params.get("password", "")
        source_folder = params.get("source_folder", "INBOX")
        target_folder = params.get("target_folder", "")
        email_ids = params.get("email_ids", [])

        error = self.validate_params(
            params, ["username", "password", "target_folder", "email_ids"]
        )
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # IMAPサーバーに接続
            with imaplib.IMAP4_SSL(imap_server, imap_port) as mail:
                mail.login(username, password)
                mail.select(source_folder)

                moved_count = 0
                for email_id in email_ids:
                    # メールをコピー
                    result = mail.copy(str(email_id), target_folder)
                    if result[0] == "OK":
                        # 元のメールに削除フラグを設定
                        mail.store(str(email_id), "+FLAGS", "\\Deleted")
                        moved_count += 1

                # 削除を確定
                mail.expunge()

            self.log(
                f"Moved {moved_count} emails from {source_folder} to {target_folder}"
            )

            return OperationResult(
                status="success",
                data={
                    "moved_count": moved_count,
                    "source_folder": source_folder,
                    "target_folder": target_folder,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to move emails: {str(e)}"
            )


class EmailSearchOperation(BaseOperation):
    """メール検索"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        imap_server = params.get("imap_server", "imap.gmail.com")
        imap_port = params.get("imap_port", 993)
        username = params.get("username", "")
        password = params.get("password", "")
        folder = params.get("folder", "INBOX")
        from_address = params.get("from_address", "")
        subject_contains = params.get("subject_contains", "")
        body_contains = params.get("body_contains", "")
        date_from = params.get("date_from", "")
        date_to = params.get("date_to", "")
        max_results = params.get("max_results", 50)
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["username", "password"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # IMAPサーバーに接続
            with imaplib.IMAP4_SSL(imap_server, imap_port) as mail:
                mail.login(username, password)
                mail.select(folder)

                # 検索条件を構築
                search_criteria = []
                if from_address:
                    search_criteria.append(f'FROM "{from_address}"')
                if subject_contains:
                    search_criteria.append(f'SUBJECT "{subject_contains}"')
                if date_from:
                    search_criteria.append(f"SINCE {date_from}")
                if date_to:
                    search_criteria.append(f"BEFORE {date_to}")

                # 検索条件がない場合は全て
                criteria_str = " ".join(search_criteria) if search_criteria else "ALL"

                # メールを検索
                status, messages = mail.search(None, criteria_str)
                if status != "OK":
                    return OperationResult(
                        status="failure", data={}, error="Failed to search emails"
                    )

                # メールIDリストを取得
                email_ids = messages[0].split()
                email_ids = (
                    email_ids[-max_results:]
                    if len(email_ids) > max_results
                    else email_ids
                )

                # 検索結果を作成
                results = []
                for email_id in email_ids:
                    status, msg_data = mail.fetch(email_id, "(BODY.PEEK[HEADER])")
                    if status != "OK":
                        continue

                    raw_header = msg_data[0][1]
                    msg = email.message_from_bytes(raw_header)

                    # body_containsでフィルタリング（必要な場合）
                    if body_contains:
                        status, body_data = mail.fetch(email_id, "(BODY[TEXT])")
                        if status == "OK":
                            body = body_data[0][1].decode("utf-8", errors="ignore")
                            if body_contains.lower() not in body.lower():
                                continue

                    results.append(
                        {
                            "id": email_id.decode(),
                            "from": msg.get("From"),
                            "subject": msg.get("Subject"),
                            "date": msg.get("Date"),
                        }
                    )

                # ストレージに保存
                if storage_key:
                    self.set_storage(storage_key, results)

            self.log(f"Found {len(results)} emails matching criteria")

            return OperationResult(
                status="success",
                data={
                    "results": results,
                    "count": len(results),
                    "search_criteria": criteria_str,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to search emails: {str(e)}"
            )
