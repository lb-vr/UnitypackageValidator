import os
import dataclasses
import generator

from PySide2.QtWidgets import (
    QCheckBox,
    QTreeView,
    QPushButton
)


def run(assets: dict, rule: dict):
    pass


@dataclasses.dataclass(eq=False)
class Generator(generator.GeneratorBase):
    cbEnable: QCheckBox
    tvAssetsList: QTreeView
    btAddUnitypackage: QPushButton
    btRemoveUnitypackage: QPushButton

    def __post_init__(self):
        pass

    @classmethod
    def getTitle(cls):
        return "同梱禁止アセット"

    @classmethod
    def getUiPath(cls) -> str:
        return os.path.join(os.path.dirname(__file__), "included_assets_filter.ui")

    def toDict(self) -> dict:
        return {
            "included_assets_filter": {
                "enabled": self.cbEnable.isChecked(),
                "values": []
            }
        }
