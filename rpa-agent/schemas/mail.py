"""
M. メール操作のスキーマ定義
"""

from .base import OperationTemplate


class MailOperations:
    """メール操作の定義"""

    @staticmethod
    def send_email() -> OperationTemplate:
        """メールを送信"""
        return OperationTemplate(
            specific_params={
                "server": "",  # 任意設定項目（用途に応じて指定）
                "protocol": "STARTTLS",  # 任意設定項目（用途に応じて指定）
                "port": 587,  # 任意設定項目（用途に応じて指定）
                "sender": "",  # 任意設定項目（用途に応じて指定）
                "login": "",  # 任意設定項目（用途に応じて指定）
                "password_type": "type-empty",  # 任意設定項目（用途に応じて指定）
                "ciphertext": "",  # 任意設定項目（用途に応じて指定）
                "nonce": "",  # 任意設定項目（用途に応じて指定）
                "encryption": 1,  # 任意設定項目（用途に応じて指定）
                "receiver": "",  # 任意設定項目（用途に応じて指定）
                "receiver_cc": "",  # 任意設定項目（用途に応じて指定）
                "receiver_bcc": "",  # 任意設定項目（用途に応じて指定）
                "subject": "",  # 任意設定項目（用途に応じて指定）
                "body": "",  # 任意設定項目（用途に応じて指定）
                "attachment": [],  # 任意設定項目（用途に応じて指定）
                "skip_file": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def receive_emails() -> OperationTemplate:
        """メール受信"""
        return OperationTemplate(
            specific_params={
                "server": "",  # 任意設定項目（用途に応じて指定）
                "protocol": "SSL/TLS",  # 任意設定項目（用途に応じて指定）
                "port": 993,  # 任意設定項目（用途に応じて指定）
                "receiver": "",  # 任意設定項目（用途に応じて指定）
                "password_type": "type-empty",  # 任意設定項目（用途に応じて指定）
                "ciphertext": "",  # 任意設定項目（用途に応じて指定）
                "nonce": "",  # 任意設定項目（用途に応じて指定）
                "encryption": 1,  # 任意設定項目（用途に応じて指定）
                "filters": [],  # 任意設定項目（用途に応じて指定）
                "attachments_path": "",  # 任意設定項目（用途に応じて指定）
                "unread_only": True,  # True/False - 任意設定項目（用途に応じて指定）
                "mark_read": False,  # True/False - 任意設定項目（用途に応じて指定）
                "mark_flag": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def send_email_gmail() -> OperationTemplate:
        """メールを送信（Gmail）"""
        return OperationTemplate(
            specific_params={
                "login": "",  # 任意設定項目（用途に応じて指定）
                "receiver": "",  # 任意設定項目（用途に応じて指定）
                "receiver_cc": "",  # 任意設定項目（用途に応じて指定）
                "receiver_bcc": "",  # 任意設定項目（用途に応じて指定）
                "subject": "",  # 任意設定項目（用途に応じて指定）
                "body": "",  # 任意設定項目（用途に応じて指定）
                "attachment": [],  # 任意設定項目（用途に応じて指定）
                "skip_file": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def receive_emails_gmail() -> OperationTemplate:
        """メール受信（Gmail）"""
        return OperationTemplate(
            specific_params={
                "receiver": "",  # 任意設定項目（用途に応じて指定）
                "filters": [],  # 任意設定項目（用途に応じて指定）
                "attachments_path": "",  # 任意設定項目（用途に応じて指定）
                "unread_only": True,  # True/False - 任意設定項目（用途に応じて指定）
                "mark_read": False,  # True/False - 任意設定項目（用途に応じて指定）
                "mark_flag": False,  # True/False - 任意設定項目（用途に応じて指定）
                "dl_inline": False,  # True/False - 任意設定項目（用途に応じて指定）
                "dl_not_multipart": True,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def send_email_microsoft() -> OperationTemplate:
        """メールを送信（Microsoft）"""
        return OperationTemplate(
            specific_params={
                "login": "",  # 任意設定項目（用途に応じて指定）
                "receiver": "",  # 任意設定項目（用途に応じて指定）
                "receiver_cc": "",  # 任意設定項目（用途に応じて指定）
                "receiver_bcc": "",  # 任意設定項目（用途に応じて指定）
                "subject": "",  # 任意設定項目（用途に応じて指定）
                "body": "",  # 任意設定項目（用途に応じて指定）
                "attachment": [],  # 任意設定項目（用途に応じて指定）
                "skip_file": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def receive_emails_microsoft() -> OperationTemplate:
        """メール受信（Microsoft）"""
        return OperationTemplate(
            specific_params={
                "receiver": "",  # 任意設定項目（用途に応じて指定）
                "filters": [],  # 任意設定項目（用途に応じて指定）
                "attachments_path": "",  # 任意設定項目（用途に応じて指定）
                "unread_only": True,  # True/False - 任意設定項目（用途に応じて指定）
                "mark_read": False,  # True/False - 任意設定項目（用途に応じて指定）
                "mark_flag": False,  # True/False - 任意設定項目（用途に応じて指定）
            }
        )