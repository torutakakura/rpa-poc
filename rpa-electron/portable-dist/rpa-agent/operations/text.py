"""
H_テキスト カテゴリの操作
"""

import re
from typing import Any, Dict

from .base import BaseOperation, OperationResult


class TextConcatOperation(BaseOperation):
    """文字列結合"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        texts = params.get("texts", [])
        separator = params.get("separator", "")
        storage_key = params.get("storage_key", "")

        if not texts:
            return OperationResult(
                status="failure", data={}, error="No texts provided to concatenate"
            )

        try:
            # 文字列を結合
            result = separator.join(str(text) for text in texts)

            if storage_key:
                self.set_storage(storage_key, result)
                self.log(f"Stored concatenated text as '{storage_key}'")

            return OperationResult(
                status="success",
                data={"result": result, "count": len(texts), "separator": separator},
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to concatenate texts: {str(e)}",
            )


class TextSplitOperation(BaseOperation):
    """文字列分割"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        delimiter = params.get("delimiter", ",")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 文字列を分割
            result = text.split(delimiter)

            if storage_key:
                self.set_storage(storage_key, result)
                self.log(f"Stored split text as '{storage_key}'")

            return OperationResult(
                status="success",
                data={"result": result, "count": len(result), "delimiter": delimiter},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to split text: {str(e)}"
            )


class TextReplaceOperation(BaseOperation):
    """文字列置換"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        search = params.get("search", "")
        replace = params.get("replace", "")
        case_sensitive = params.get("case_sensitive", True)
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text", "search"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 大文字小文字を区別しない場合
            if not case_sensitive:
                result = re.sub(re.escape(search), replace, text, flags=re.IGNORECASE)
            else:
                result = text.replace(search, replace)

            if storage_key:
                self.set_storage(storage_key, result)
                self.log(f"Stored replaced text as '{storage_key}'")

            return OperationResult(
                status="success",
                data={
                    "result": result,
                    "original": text,
                    "search": search,
                    "replace": replace,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to replace text: {str(e)}"
            )


class TextExtractOperation(BaseOperation):
    """部分文字列抽出"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        start = params.get("start", 0)
        end = params.get("end")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # 部分文字列を抽出
            result = text[start:] if end is None else text[start:end]

            if storage_key:
                self.set_storage(storage_key, result)
                self.log(f"Stored extracted text as '{storage_key}'")

            return OperationResult(
                status="success",
                data={
                    "result": result,
                    "start": start,
                    "end": end,
                    "length": len(result),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to extract text: {str(e)}"
            )


class TextLengthOperation(BaseOperation):
    """文字列長を取得"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            length = len(text)

            if storage_key:
                self.set_storage(storage_key, length)
                self.log(f"Stored text length as '{storage_key}': {length}")

            return OperationResult(
                status="success",
                data={
                    "length": length,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to get text length: {str(e)}"
            )


class TextCaseOperation(BaseOperation):
    """大文字・小文字変換"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        case_type = params.get("case_type", "upper")  # upper, lower, title, capitalize
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            if case_type == "upper":
                result = text.upper()
            elif case_type == "lower":
                result = text.lower()
            elif case_type == "title":
                result = text.title()
            elif case_type == "capitalize":
                result = text.capitalize()
            else:
                return OperationResult(
                    status="failure", data={}, error=f"Unknown case type: {case_type}"
                )

            if storage_key:
                self.set_storage(storage_key, result)
                self.log(f"Stored converted text as '{storage_key}'")

            return OperationResult(
                status="success",
                data={"result": result, "case_type": case_type, "original": text},
            )
        except Exception as e:
            return OperationResult(
                status="failure",
                data={},
                error=f"Failed to convert text case: {str(e)}",
            )


class TextTrimOperation(BaseOperation):
    """文字列トリム（前後の空白削除）"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        trim_type = params.get("trim_type", "both")  # both, left, right
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            if trim_type == "both":
                result = text.strip()
            elif trim_type == "left":
                result = text.lstrip()
            elif trim_type == "right":
                result = text.rstrip()
            else:
                return OperationResult(
                    status="failure", data={}, error=f"Unknown trim type: {trim_type}"
                )

            if storage_key:
                self.set_storage(storage_key, result)
                self.log(f"Stored trimmed text as '{storage_key}'")

            return OperationResult(
                status="success",
                data={
                    "result": result,
                    "trim_type": trim_type,
                    "original_length": len(text),
                    "result_length": len(result),
                },
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to trim text: {str(e)}"
            )


class RegexMatchOperation(BaseOperation):
    """正規表現マッチング"""

    async def execute(self, params: Dict[str, Any]) -> OperationResult:
        text = params.get("text", "")
        pattern = params.get("pattern", "")
        flags = params.get("flags", [])  # ['IGNORECASE', 'MULTILINE', etc.]
        storage_key = params.get("storage_key", "")

        error = self.validate_params(params, ["text", "pattern"])
        if error:
            return OperationResult(status="failure", data={}, error=error)

        try:
            # フラグを設定
            regex_flags = 0
            for flag in flags:
                if flag == "IGNORECASE":
                    regex_flags |= re.IGNORECASE
                elif flag == "MULTILINE":
                    regex_flags |= re.MULTILINE
                elif flag == "DOTALL":
                    regex_flags |= re.DOTALL

            # マッチング実行
            matches = re.findall(pattern, text, flags=regex_flags)

            if storage_key:
                self.set_storage(storage_key, matches)
                self.log(f"Stored regex matches as '{storage_key}'")

            return OperationResult(
                status="success",
                data={"matches": matches, "count": len(matches), "pattern": pattern},
            )
        except Exception as e:
            return OperationResult(
                status="failure", data={}, error=f"Failed to match regex: {str(e)}"
            )
