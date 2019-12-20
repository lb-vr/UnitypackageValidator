import sys
import os

# PySide2
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

from rule_generator.main_ui import MainWindow


def rule_generator_main():

    # アプリケーション作成
    app = QApplication(sys.argv)

    # オブジェクト作成
    window = MainWindow()

    # MainWindowの表示
    window.show()
    sys.exit(app.exec_())
