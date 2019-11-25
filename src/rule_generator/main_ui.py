import os
import webbrowser
import re
import tempfile
import logging
# import pyperclip

from typing import List, Tuple, Optional, Dict, Any

from PySide2.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QTreeWidgetItem, QFormLayout, QLineEdit, QLabel
from PySide2.QtWidgets import QTreeWidget, QSpinBox, QCheckBox, QComboBox, QHBoxLayout, QPushButton, QSizePolicy, QProgressBar
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
        self.__is_catch_item_changed = True

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

    def addActionsForUnitypackageButton(self, component_name_list: List[str]):
        """
        シグナルを接続するためのユーティリティー関数
        Unitypackageを読み込んで、TreeWidgetに表示させる動作を登録する
        """
        for n in component_name_list:
            cmp_add_name: str = n + "_AddPkg"
            cmp_del_name: str = n + "_DelPkg"
            cmp_trw_name: str = n + "_tw"

            assert hasattr(self.ui, cmp_trw_name)
            assert hasattr(self.ui, cmp_add_name)
            assert hasattr(self.ui, cmp_del_name)

            getattr(self.ui, cmp_add_name).clicked.connect(
                lambda: self.addUnitypackage(getattr(self.ui, cmp_trw_name)))
            getattr(self.ui, cmp_trw_name).itemChanged.connect(
                lambda itm, clm: self.changedTreeWidgetItem(
                    getattr(self.ui, cmp_trw_name), itm, clm))

    def addUnitypackage(self, target_treewidget: QTreeWidget):
        """
        実際にUnitypackageを読み込んで、TreeWidgetに登録する
        TODO: 既に読み込まれたunitypackageをルートノードから判別して、新規のもののみに絞る
        """
        self.logger.debug("Adding an unitypackage.")
        ret = QFileDialog.getOpenFileName(self, "ファイルを開く", "/", "Unitypackage (*.unitypackage)")
        if ret[0]:
            unitypackage_fpath = ret[0]
            unity_package: Unitypackage = Unitypackage(os.path.basename(unitypackage_fpath))

            # TODO: target_treewidgetのすべての子のdataを調査し、同じunitypackageが既にインポートされていないかチェックする
            for rc_index in range(target_treewidget.topLevelItemCount()):
                itm: QTreeWidgetItem = target_treewidget.topLevelItem(rc_index)
                dt = itm.data(0, QtCore.Qt.UserRole)
                if type(dt) is Unitypackage:
                    if dt.name == unity_package.name:
                        QMessageBox.warning(None, "警告", "{0.name}\nこのunitypackageは既に読み込み済みです".format(unity_package))
                        return

            self.logger.debug("- Loading an unitypackage. The unitypackage filepath is %s", unitypackage_fpath)
            with tempfile.TemporaryDirectory() as tmpdir:
                self.logger.debug("- Temporary directory path is %s", tmpdir)

                # Extract
                Unitypackage.extract(unitypackage_fpath, tmpdir)

                # load
                unity_package.load(tmpdir)

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
                pathobj = [{}, unity_package]
                for asset in unity_package.assets.values():
                    if asset.path.startswith("Assets/"):
                        splitted_path = asset.path.split("/")[1:]
                        _path(pathobj, splitted_path, asset)

                # ----------------------------------------------
                # unitypackageからTreeWidgetへ追加
                def _addTreeWidget(upkg_name, target, obj):
                    for k, v in obj.items():
                        item = QTreeWidgetItem(target)
                        item.setText(0, k)
                        item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                        item.setText(2, upkg_name)
                        if v[1]:
                            item.setData(0, QtCore.Qt.UserRole, v[1])
                            if type(v[1]) is Asset:
                                item.setText(1, v[1].guid)
                        if v[0]:
                            _addTreeWidget(upkg_name, item, v[0])

                self.__is_catch_item_changed = False
                _addTreeWidget(unity_package.name, target_treewidget, {unity_package.name: pathobj})
                self.__is_catch_item_changed = True

    def changedTreeWidgetItem(self, tree_widget: QTreeWidget, item: QTreeWidgetItem, column: int):
        if not self.__is_catch_item_changed:
            return

        if column == 0:
            check_state: QtCore.Qt.CheckState = item.checkState(0)

            if check_state == QtCore.Qt.CheckState.Unchecked or check_state == QtCore.Qt.CheckState.Checked:
                for child_index in range(item.childCount()):
                    if item.child(child_index).checkState(0) != check_state:
                        item.child(child_index).setCheckState(0, check_state)
            elif check_state == QtCore.Qt.CheckState.PartiallyChecked:
                pass

            parent = item.parent()
            if parent:
                parent_check_state = None
                for child_index in range(parent.childCount()):
                    if parent_check_state is not None and parent_check_state != parent.child(child_index).checkState(0):
                        parent_check_state = QtCore.Qt.CheckState.PartiallyChecked
                        break

                    parent_check_state = parent.child(child_index).checkState(0)

                if parent_check_state is not None:
                    parent.setCheckState(0, parent_check_state)
