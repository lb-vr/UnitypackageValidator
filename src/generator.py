import os
import dataclasses
from ui_loader import UiContainer
from PySide2.QtWidgets import (
    QMainWindow,
    QTabWidget
)
from PySide2.QtGui import (
    QIcon
)

from rules import rule_loader


@dataclasses.dataclass
class GeneratorBase(UiContainer):
    pass


@dataclasses.dataclass
class GeneratorUi(UiContainer):
    ruleTab: QTabWidget


class GeneratorWindow(QMainWindow):
    def __init__(self, args, parent=None):
        # UI初期化処理
        super().__init__(parent)
        self.ui: GeneratorUi = GeneratorUi.load(os.path.join(os.path.dirname(__file__), "ui/generator.ui"),
                                                root_widget=self)
        self.setWindowTitle('Validator v0.0.1')

        self.generators = []

        for gen in rule_loader.getGenerators():
            print(gen.getUiPath())
            generator_instance = gen.load(gen.getUiPath(), root_widget=None)
            self.generators.append(generator_instance)
            print(type(generator_instance.widgets), generator_instance.widgets)
            self.ui.ruleTab.addTab(generator_instance.widgets, gen.getTitle())
