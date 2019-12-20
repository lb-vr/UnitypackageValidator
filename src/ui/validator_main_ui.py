import os
import webbrowser
import re
import tempfile
import logging
import datetime
import json
import configparser
# import pyperclip


import sys
import os

# PySide2
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon

from typing import List, Tuple, Optional, Dict, Any

import queue

import webbrowser

from PySide2.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QTreeWidgetItem, QFormLayout, QLineEdit, QLabel
from PySide2.QtWidgets import QTreeWidget, QSpinBox, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QSizePolicy
from PySide2.QtWidgets import QListWidgetItem, QProgressBar, QListWidget
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader

# import internal modules
from unitypackage import Unitypackage, Asset
from validators.core import Validator


class MainWindow(QMainWindow):

    def __init__(self, args, parent=None):

        # UI初期化処理
        super(MainWindow, self).__init__(parent)
        self.ui = QUiLoader().load('ui/validator2.ui')
        self.setCentralWidget(self.ui)
        self.setWindowTitle('Validator v0.0.1')

        # ロガー
        self.__logger: logging.Logger = logging.getLogger("MainWindow")

        # 設定ファイルを読み込む
        ini = configparser.ConfigParser()
        args.config = os.path.abspath(args.config)
        if not os.path.exists(args.config):
            raise FileNotFoundError(args.config)
        ini.read(args.config, "UTF-8")
        print(ini)
        self.ui.tbExhibitorId.setText(ini["user"]["id"])
        self.ui.tbRuleFileUrl.setText(ini["rule"]["url"])

        self.__before_opened_directory = "/"

        # シグナル
        self.ui.btOpenUnitypackage.clicked.connect(self.openUnitypackage)
        self.ui.btValidate.clicked.connect(self.doIt)
        self.ui.btUpload.clicked.connect(lambda: webbrowser.open(ini["upload"]["url"]))

        self.validator = None
        self.results = {}

    def openUnitypackage(self):
        ret = QFileDialog.getOpenFileName(
            self, "Unitypackageを開く", self.__before_opened_directory, "Unitypackage (*.unitypackage)")
        if ret[0]:
            self.__before_opened_directory = os.path.dirname(ret[0])
            self.ui.tbUnitypackageFilepath.setText(ret[0])

    def updateProgress(self, value, line):
        self.statusBar().showMessage(line)
        self.ui.progressBar.setValue(value)

    def finishedValidating(self, ret):
        # 結果を文字で出す
        message = ""
        for header, logs, notices in ret[0]:
            message += "<h1>" + header + "</h1>\n"
            for log in logs:
                message += "<p>" + log + "</p>\n"
            for notice in notices:
                message += "<p>" + notice + "</p>\n"

        self.ui.tbErrorMessage.setHtml(message)
        self.__addUnitypackage(self.ui.twBeforeUnitypackage, ret[1], True)
        self.__addUnitypackage(self.ui.twAfterUnitypackage, ret[2], False, 1)
        self.ui.btValidate.setEnabled(True)

        QMessageBox.information(None, "完了", "unitypackageのバリデーションと書き出しが完了しました")

    def doIt(self):
        # エラーチェック
        if self.ui.tbUnitypackageFilepath.text() == "":
            QMessageBox.critical(None, "エラー", "チェック対象のUnitypackageが入力されていません")
            return

        if not re.match("[a-zA-Z0-9_-]+", self.ui.tbExhibitorId.text()):
            QMessageBox.critical(None, "エラー", "出展者IDが不正です")
            return

        fpath = self.ui.tbUnitypackageFilepath.text()
        if not os.path.exists(fpath) or not os.path.isfile(fpath):
            QMessageBox.critical(None, "エラー", "入力されたUnitypackageが存在しません")
            return

        ret = QFileDialog.getExistingDirectory(
            self, "Unitypackageの保存先を選択", self.__before_opened_directory)
        if not ret:
            return

        self.__before_opened_directory = ret[0]

        # 一度データクリア
        self.ui.twBeforeUnitypackage.clear()
        self.ui.twAfterUnitypackage.clear()
        self.ui.tbErrorMessage.setText("")
        self.ui.btValidate.setEnabled(False)

        # 実行
        self.results = {}
        self.validator = Validator(fpath, self.ui.tbRuleFileUrl.text(),
                                   self.ui.tbExhibitorId.text(),
                                   os.path.join(ret, "{}.unitypackage".format(self.ui.tbExhibitorId.text())))
        self.validator.finishedValidating.connect(self.finishedValidating)
        self.validator.progress.connect(self.updateProgress)
        self.validator.start()

    def __addUnitypackage(self, target_treewidget: QTreeWidget, unitypackage: Unitypackage, show_delete: bool,
                          show_old_guid: Optional[int] = None, show_new_guid: Optional[int] = None):
        # ----------------------------------------------
        # unitypackageのアセットをパスの形に直す
        # 再帰的解析
        def _path(target, splitted_path: List[str], asset: Asset):
            if len(splitted_path) == 0:
                target[1] = asset
            else:
                if splitted_path[0] not in target[0]:
                    target[0][splitted_path[0]] = [{}, None]
                _path(target[0][splitted_path[0]], splitted_path[1:], asset)

        # ただしAssets/は抜く
        pathobj = [{}, unitypackage]
        for asset in unitypackage.assets.values():
            if asset.deleted and not show_delete:
                continue

            if asset.path.startswith("Assets/"):
                splitted_path = asset.path.split("/")[1:]
                _path(pathobj, splitted_path, asset)

        # ----------------------------------------------
        # unitypackageからTreeWidgetへ追加
        def _addTreeWidget(upkg_name, target, obj,
                           show_old_guid: Optional[int] = None, show_new_guid: Optional[int] = None):
            for k, v in obj.items():
                item = QTreeWidgetItem(target)
                item.setText(0, k)
                if v[1]:
                    if type(v[1]) is Asset:
                        if v[1].deleted:
                            item.setText(1, "削除されました")
                            # item.setEnabled(False)
                        if show_old_guid:
                            item.setText(show_old_guid, asset.guid)
                if v[0]:
                    _addTreeWidget(upkg_name, item, v[0], show_old_guid, show_new_guid)

        _addTreeWidget(unitypackage.name, target_treewidget, pathobj[0], show_old_guid, show_new_guid)


def validator_main_ui(args):

    # アプリケーション作成
    app = QApplication(sys.argv)

    # オブジェクト作成
    window = MainWindow(args)

    # MainWindowの表示
    window.show()
    sys.exit(app.exec_())
