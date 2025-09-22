"""
C. マウス操作のスキーマ定義
"""

from .base import OperationTemplate


class MouseOperations:
    """マウス操作の定義"""

    class Move:
        @staticmethod
        def move_mouse_to_absolute_coordinates() -> OperationTemplate:
            """マウス移動（座標）"""
            return OperationTemplate(
                specific_params={
                    "x": 100,  # 任意設定項目（用途に応じて指定）
                    "y": 100,  # 任意設定項目（用途に応じて指定）
                    "click": "single",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def move_mouse_to_relative_coordinates() -> OperationTemplate:
            """マウス移動（距離）"""
            return OperationTemplate(
                specific_params={
                    "x": 100,  # 任意設定項目（用途に応じて指定）
                    "y": 100,  # 任意設定項目（用途に応じて指定）
                    "click": "single",  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def move_mouse_to_image() -> OperationTemplate:
            """マウス移動（画像認識）"""
            return OperationTemplate(
                specific_params={
                    "filename": "",  # 任意設定項目（用途に応じて指定）
                    "precision": 85,  # 画像一致の厳しさ（%）
                    "noise_filter": 100.0,  # 画像検索時のノイズ除去率
                    "search_area_type": None,  # screen/window/area - 検索範囲の種類
                    "search_area": "(0,0)-(0,0)",  # rect (x1,y1)-(x2,y2) - 検索座標の範囲指定
                    "click": "single",  # 任意設定項目（用途に応じて指定）
                }
            )

    class DragAndDrop:
        @staticmethod
        def drag_and_drop_to_absolute_coordinates() -> OperationTemplate:
            """現在位置からドラッグ&ドロップ（座標）"""
            return OperationTemplate(
                specific_params={
                    "x": 100,  # 任意設定項目（用途に応じて指定）
                    "y": 100,  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def drag_and_drop_to_relative_coordinates() -> OperationTemplate:
            """現在位置からドラッグ&ドロップ（距離）"""
            return OperationTemplate(
                specific_params={
                    "x": 100,  # 任意設定項目（用途に応じて指定）
                    "y": 100,  # 任意設定項目（用途に応じて指定）
                }
            )

        @staticmethod
        def drag_and_drop_to_image() -> OperationTemplate:
            """現在位置からドラッグ&ドロップ（画像認識）"""
            return OperationTemplate(
                specific_params={
                    "filename": "",  # 任意設定項目（用途に応じて指定）
                    "precision": 85,  # 画像一致の厳しさ（%）
                    "noise_filter": 100.0,  # 画像検索時のノイズ除去率
                    "search_area_type": None,  # screen/window/area - 検索範囲の種類
                    "search_area": "(0,0)-(0,0)",  # rect (x1,y1)-(x2,y2) - 検索座標の範囲指定
                }
            )

    @staticmethod
    def click_mouse() -> OperationTemplate:
        """マウスクリック"""
        return OperationTemplate(
            specific_params={
                "type": "single",  # 任意設定項目（用途に応じて指定）
                "key": "__null__",  # 任意設定項目（用途に応じて指定）
            }
        )

    @staticmethod
    def scroll_mouse() -> OperationTemplate:
        """マウススクロール"""
        return OperationTemplate(
            specific_params={
                "direction": "up",  # 任意設定項目（用途に応じて指定）
                "amount": 3,  # 任意設定項目（用途に応じて指定）
            }
        )
