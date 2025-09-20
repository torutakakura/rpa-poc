"""
C. マウス操作のスキーマ定義
"""

from .base import OperationTemplate


class MouseOperations:
    """マウス操作の定義"""

    class Move:
        @staticmethod
        def by_coordinates() -> OperationTemplate:
            """座標"""
            return OperationTemplate(
                specific_params={"x": 0, "y": 0, "move_speed": "normal"}
            )

        @staticmethod
        def by_distance() -> OperationTemplate:
            """距離"""
            return OperationTemplate(
                specific_params={"dx": 0, "dy": 0, "move_speed": "normal"}
            )

        @staticmethod
        def by_image() -> OperationTemplate:
            """画像認識"""
            return OperationTemplate(
                specific_params={
                    "image_path": "",
                    "accuracy": 0.8,
                    "click_position": "center",
                    "offset_x": 0,
                    "offset_y": 0,
                }
            )

    class DragAndDrop:
        @staticmethod
        def by_coordinates() -> OperationTemplate:
            """座標（D&D）"""
            return OperationTemplate(
                specific_params={
                    "start_x": 0,
                    "start_y": 0,
                    "end_x": 0,
                    "end_y": 0,
                    "drag_speed": "normal",
                }
            )

        @staticmethod
        def by_distance() -> OperationTemplate:
            """距離（D&D）"""
            return OperationTemplate(
                specific_params={"dx": 0, "dy": 0, "drag_speed": "normal"}
            )

        @staticmethod
        def by_image() -> OperationTemplate:
            """画像認識（D&D）"""
            return OperationTemplate(
                specific_params={
                    "start_image_path": "",
                    "end_image_path": "",
                    "accuracy": 0.8,
                    "drag_speed": "normal",
                }
            )

    @staticmethod
    def click() -> OperationTemplate:
        """マウスクリック"""
        return OperationTemplate(
            specific_params={
                "button": "left",
                "click_type": "single",
                "x": None,
                "y": None,
            }
        )

    @staticmethod
    def scroll() -> OperationTemplate:
        """スクロール"""
        return OperationTemplate(specific_params={"direction": "down", "amount": 3})
