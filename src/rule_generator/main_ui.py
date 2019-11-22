import os
import webbrowser
import re
import tempfile
import logging
# import pyperclip

from typing import List, Tuple, Optional, Dict, Any

from PySide2.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QTreeWidgetItem, QFormLayout, QLineEdit, QLabel, QFrame, QSpinBox, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QSizePolicy, QProgressBar
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtUiTools import QUiLoader

# import internal modules
from unitypackage import Unitypackage, Asset


class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        # UI初期化処理
        super(MainWindow, self).__init__(parent)
        self.ui = QUiLoader().load(os.path.abspath('../../ui/rule_generator3.ui'))
        self.setCentralWidget(self.ui)
        self.setWindowTitle('Rule Generator v0.0.1')

        # ロガー
        self.__logger: logging.Logger = logging.getLogger("MainWindow")

        # ボタン
        self.addActionsForUnitypackageButton(["IncludesBlacklist"])

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

    def addActionsForUnitypackageButton(self, component_name_list: List[str]):
        for n in component_name_list:
            cmp_add_name: str = n + "_AddPkg"
            cmp_del_name: str = n + "_DelPkg"
            cmp_trw_name: str = n + "_tw"

            assert hasattr(self.ui, cmp_trw_name)
            assert hasattr(self.ui, cmp_add_name)
            assert hasattr(self.ui, cmp_del_name)

            getattr(self.ui, cmp_add_name).clicked.connect(
                lambda: self.addUnitypackage(getattr(self. ui, cmp_trw_name)))

    def addUnitypackage(self, target_treewidget):
        # プログレスバーをセット
        bar = QProgressBar()
        self.statusBar().addWidget(bar)

        # 処理開始
        self.logger.debug("Adding an unitypackage.")
        ret = QFileDialog.getOpenFileName(self, "ファイルを開く", "/", "Unitypackage (*.unitypackage)")
        if ret[0]:
            unitypackage_fpath = ret[0]
            self.logger.debug("- Loading an unitypackage. The unitypackage filepath is %s", unitypackage_fpath)
            with tempfile.TemporaryDirectory() as tmpdir:
                self.logger.debug("- Temporary directory path is %s", tmpdir)
                self.statusBar().showMessage("Unitypackageの解凍中...")
                bar.setValue(30)

                # Extract
                Unitypackage.extract(unitypackage_fpath, tmpdir)
                self.statusBar().showMessage("Unitypackageの読み込み中...")
                bar.setValue(60)

                # load
                unity_package: Unitypackage = Unitypackage(os.path.basename(unitypackage_fpath))
                unity_package.load(tmpdir)
                bar.setValue(80)

                # ----------------------------------------------
                # unitypackageのアセットをパスの形に直す
                # 再帰的解析
                def _path(target: dict, splitted_path: List[str], asset: Asset):
                    assert len(splitted_path) > 0
                    if len(splitted_path) == 1:
                        print("assign asset " + str(asset) + " to path : " + splitted_path[0])
                        target[splitted_path[0]] = asset
                    else:
                        if splitted_path[0] not in target:
                            target[splitted_path[0]] = {}
                        _path(target[splitted_path[0]], splitted_path[1:], asset)

                # ただしAssets/は抜く
                pathobj: dict = {}
                for asset in unity_package.assets.values():
                    if asset.path.startswith("Assets/"):
                        splitted_path = asset.path.split("/")[1:]
                        _path(pathobj, splitted_path, asset)

                # ----------------------------------------------
                # unitypackageからTreeWidgetへ追加
                # TODO: Directoryどうしよう
                def _addTreeWidget(upkg_name, target, dict_: dict):
                    for k, v in dict_.items():
                        item = QTreeWidgetItem(target)
                        item.setText(0, k)
                        item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                        item.setText(2, upkg_name)
                        if type(v) is Asset:
                            item.setData(0, QtCore.Qt.UserRole, v)
                            item.setText(1, v.guid)
                            self.logger.debug("Add TreeWidget. Target is %s, Asset is %s", target, v)
                        else:
                            _addTreeWidget(upkg_name, item, v)
                self.logger.debug("- Target Widget is %s", target_treewidget)
                _addTreeWidget(unity_package.name, target_treewidget, pathobj)

        self.statusBar().removeWidget(bar)
