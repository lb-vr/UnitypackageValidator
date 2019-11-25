import os
import webbrowser
import re
import tempfile
import logging
import datetime
import json
# import pyperclip

from typing import List, Tuple, Optional, Dict, Any


from PySide2.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QTreeWidgetItem, QFormLayout, QLineEdit, QLabel
from PySide2.QtWidgets import QTreeWidget, QSpinBox, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QSizePolicy
from PySide2.QtWidgets import QListWidgetItem, QProgressBar, QListWidget
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader

# import internal modules
from unitypackage import Unitypackage, Asset


class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        # UI初期化処理
        super(MainWindow, self).__init__(parent)
        self.ui = QUiLoader().load(os.path.abspath('../../ui/validator.ui'))
        self.setCentralWidget(self.ui)
        self.setWindowTitle('Unitypackage Validator v0.0.1')

        # ロガー
        self.__logger: logging.Logger = logging.getLogger("MainWindow")

    @property
    def logger(self) -> logging.Logger:
        return self.__logger
