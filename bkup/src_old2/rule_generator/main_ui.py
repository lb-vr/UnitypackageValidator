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
        self.ui = QUiLoader().load(os.path.abspath('ui/rule_generator3.ui'))
        self.setCentralWidget(self.ui)
        self.setWindowTitle('Rule Generator v0.0.1')

        # ロガー
        self.__logger: logging.Logger = logging.getLogger("MainWindow")

        # ボタン
        self.ui.FileBlacklist_Add.clicked.connect(self.clickedAddFileBlacklist)
        self.ui.FileBlacklist_Del.clicked.connect(self.clickedDeleteFileBlacklist)
        self.ui.IncludesBlacklist_AddPkg.clicked.connect(self.clickedAddIncludesBlacklist)
        self.ui.IncludesBlacklist_DelPkg.clicked.connect(self.clickedDeleteIncludesBlacklist)
        self.ui.ModifiableAsset_AddPkg.clicked.connect(self.clickedAddModifiableAsset)
        self.ui.ModifiableAsset_DelPkg.clicked.connect(self.clickedDeleteModifiableAsset)
        self.ui.CommonAsset_AddPkg.clicked.connect(self.clickedAddCommonAsset)
        self.ui.CommonAsset_DelPkg.clicked.connect(self.clickedDeleteCommonAsset)
        self.ui.BuiltinCGIncludes_Add.clicked.connect(self.clickedAddBuiltinCGIncludes)
        self.ui.BuiltinCGIncludes_Del.clicked.connect(self.clickedDeleteBuiltinCGIncludes)

        # TreeWidget
        self.ui.IncludesBlacklist_tw.itemChanged.connect(self.itemChangedIncludesBlacklist)
        self.ui.ModifiableAsset_tw.itemChanged.connect(self.itemChangedModifiableAsset)
        self.ui.CommonAsset_tw.itemChanged.connect(self.itemChangedCommonAsset)

        # トリガー
        self.ui.actionExport.triggered.connect(self.export)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionOpen.triggered.connect(self.open)

        self.__is_catch_item_changed = True

        self.__before_opened_directory = "/"

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

    #####
    # イベントハンドラ
    #####

    def clickedAddIncludesBlacklist(self):
        self.addUnitypackage(self.ui.IncludesBlacklist_tw)

    def clickedAddModifiableAsset(self):
        self.addUnitypackage(self.ui.ModifiableAsset_tw)

    def clickedAddCommonAsset(self):
        self.addUnitypackage(self.ui.CommonAsset_tw)

    def clickedAddBuiltinCGIncludes(self):
        self.logger.debug("Adding built-in cginc files by file browser.")
        ret = QFileDialog.getOpenFileNames(self, "ビルトインCGIncludesファイルを開く", self.__before_opened_directory,
                                           "CGInclude (*.cginc *.glslinc)")
        if ret is not None:
            if len(ret[0]) > 0:
                self.__before_opened_directory = os.path.dirname(ret[0][0])
            for f in ret[0]:
                # すでに追加されていないか
                if not self.ui.BuiltinCGIncludes_list.findItems(os.path.basename(f), QtCore.Qt.MatchExactly):
                    itm: QListWidgetItem = QListWidgetItem(self.ui.BuiltinCGIncludes_list)
                    itm.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled |
                                 QtCore.Qt.ItemFlag.ItemIsEditable |
                                 QtCore.Qt.ItemFlag.ItemIsSelectable)
                    itm.setText(os.path.basename(f))

    def clickedDeleteBuiltinCGIncludes(self):
        row: int = self.ui.BuiltinCGIncludes_list.currentRow()
        self.ui.BuiltinCGIncludes_list.takeItem(row)

    def clickedDeleteIncludesBlacklist(self):
        self.deleteUnitypackage(self.ui.IncludesBlacklist_tw)

    def clickedDeleteModifiableAsset(self):
        self.deleteUnitypackage(self.ui.ModifiableAsset_tw)

    def clickedDeleteCommonAsset(self):
        self.deleteUnitypackage(self.ui.CommonAsset_tw)

    def itemChangedIncludesBlacklist(self, itm: QTreeWidgetItem, clm: int):
        self.changedTreeWidgetItem(self.ui.IncludesBlacklist_tw, itm, clm)

    def itemChangedModifiableAsset(self, itm: QTreeWidgetItem, clm: int):
        self.changedTreeWidgetItem(self.ui.ModifiableAsset_tw, itm, clm)

    def itemChangedCommonAsset(self, itm: QTreeWidgetItem, clm: int):
        self.changedTreeWidgetItem(self.ui.CommonAsset_tw, itm, clm)

    #####
    # 操作系
    #####

    def __addUnitypackage(self, target_treewidget: QTreeWidget, unitypackage: Unitypackage):
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
                        if v[1].enabled is not None:
                            if v[1].enabled is False:
                                item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
                        # self.changedTreeWidgetItem(target)
                if v[0]:
                    _addTreeWidget(upkg_name, item, v[0])

        # self.__is_catch_item_changed = False
        _addTreeWidget(unitypackage.name, target_treewidget, {unitypackage.name: pathobj})
        # self.__is_catch_item_changed = True

    def addUnitypackage(self, target_treewidget: QTreeWidget):
        """
        実際にUnitypackageを読み込んで、TreeWidgetに登録する
        """
        self.logger.debug("Adding an unitypackage.")
        ret = QFileDialog.getOpenFileName(
            self, "ファイルを開く", self.__before_opened_directory, "Unitypackage (*.unitypackage)")
        if ret[0]:
            unitypackage_fpath = ret[0]
            self.__before_opened_directory = os.path.dirname(ret[0])
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

                self.__addUnitypackage(target_treewidget, unity_package)

    def deleteUnitypackage(self, target_treewidget: QTreeWidget):
        QMessageBox.warning(None, "未実装", "Not implemented.")

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

    def clickedAddFileBlacklist(self):
        """
        新しいブラックリストを追加する
        """
        itm: QListWidgetItem = QListWidgetItem(self.ui.FileBlacklist_list)
        itm.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled |
                     QtCore.Qt.ItemFlag.ItemIsEditable |
                     QtCore.Qt.ItemFlag.ItemIsSelectable)
        itm.setText("<< Edit here >>")

    def clickedDeleteFileBlacklist(self):
        """
        選択したブラックリストを削除する
        """
        row: int = self.ui.FileBlacklist_list.currentRow()
        self.ui.FileBlacklist_list.takeItem(row)

    def _putItem(self, target, item: QTreeWidgetItem, for_export: bool = True):
        if item.checkState(0) != QtCore.Qt.CheckState.Unchecked or not for_export:  # PartiallyChecked or Checked
            dt = item.data(0, QtCore.Qt.UserRole)
            next_target = target
            if type(dt) is Asset:
                enabled: Optional[bool] = None if for_export else bool(
                    item.checkState(0) == QtCore.Qt.CheckState.Checked)
                target.update(dt.toDict(True, enabled))

            elif type(dt) is Unitypackage:
                target[dt.name] = {}
                next_target = target[dt.name]

            for child_index in range(item.childCount()):
                self._putItem(next_target, item.child(child_index), for_export)

    def _putTree(self, target, target_treewidget: QTreeWidget, for_export: bool = True):
        for item_index in range(target_treewidget.topLevelItemCount()):
            self._putItem(target, target_treewidget.topLevelItem(item_index), for_export)

    def _putList(self, target: list, target_listwidget: QListWidget):
        for item_index in range(target_listwidget.count()):
            target.append(target_listwidget.item(item_index).text())

    def _saveToJson(self, for_export: bool = True):
        """
        jsonへ出力する
        """
        error_msg: List[str] = []
        # TODO: ここに値がセットされているかチェック

        # BRABRA

        if error_msg and for_export:
            QMessageBox.critical(None, "エラー", "書き出しに不足しているデータがあります\n" + "\n".join(error_msg))
            return

        ret = QFileDialog.getSaveFileName(self, "ルールファイルを保存", self.__before_opened_directory, "Json (*.json)")
        if not ret[0]:
            return

        self.__before_opened_directory = os.path.dirname(ret[0])

        jsonobj = {
            "created_at": "{0:%Y-%m-%d %H:%M:%S}".format(datetime.datetime.now()),
            "author": self.ui.tbRuleAuthor.text(),
            "version": self.ui.tbRuleVersion.text() if self.ui.tbRuleVersion.text() else None,
            "event": {
                "name": self.ui.tbEventName.text(),
                "author": self.ui.tbEventAuthor.text() if self.ui.tbEventAuthor.text() else None,
                "homepage": self.ui.tbHomepageUrl.text() if self.ui.tbHomepageUrl.text() else None
            },
            "rules": {
                "includes_blacklist": {},
                "file_blacklist": [],
                "modifiable_assets": {},
                "common_assets": {},
                "builtin_cgincludes": []
            }
        }

        # includes blacklist
        self._putTree(jsonobj["rules"]["includes_blacklist"], self.ui.IncludesBlacklist_tw, for_export)
        self._putList(jsonobj["rules"]["file_blacklist"], self.ui.FileBlacklist_list)
        self._putTree(jsonobj["rules"]["modifiable_assets"], self.ui.ModifiableAsset_tw, for_export)
        self._putTree(jsonobj["rules"]["common_assets"], self.ui.CommonAsset_tw, for_export)
        self._putList(jsonobj["rules"]["builtin_cgincludes"], self.ui.BuiltinCGIncludes_list)

        # Output file
        with open(ret[0], encoding="utf-8", mode="w") as jsonf:
            json.dump(jsonobj, jsonf)

    def _gets(self, json_obj, keys: List[str], _type: Optional[type] = None, _default=None):
        if len(keys) == 0:
            if _type is not None:
                if type(json_obj) is _type:
                    return json_obj
                else:
                    return _default
            else:
                return json_obj
        else:
            if keys[0] in json_obj:
                return self._gets(json_obj[keys[0]], keys[1:], _type, _default)
            else:
                return _default

    def save(self):
        self._saveToJson(False)
        pass

    def export(self):
        self._saveToJson()

    def open(self):
        """
        jsonを解析して起こす
        """

        # 読み込むjsonを取得
        ret = QFileDialog.getOpenFileName(self, "ルールファイルを開く", self.__before_opened_directory, "Json (*.json)")
        if not ret[0]:
            return

        self.__before_opened_directory = os.path.dirname(ret[0])

        json_obj: dict = {}
        with open(ret[0], encoding="utf-8", mode="r") as jsonf:
            json_obj = json.load(jsonf)

        # 全Item削除
        self.ui.IncludesBlacklist_tw.clear()
        self.ui.FileBlacklist_list.clear()
        self.ui.ModifiableAsset_tw.clear()
        self.ui.CommonAsset_tw.clear()

        # メタデータ
        self.ui.tbRuleAuthor.setText(self._gets(json_obj, ["author"], str, ""))
        self.ui.tbRuleVersion.setText(self._gets(json_obj, ["version"], str, ""))
        self.ui.tbEventName.setText(self._gets(json_obj, ["event", "name"], str, ""))
        self.ui.tbEventAuthor.setText(self._gets(json_obj, ["event", "author"], str, ""))
        self.ui.tbHomepageUrl.setText(self._gets(json_obj, ["event", "homepage"], str, ""))

        # TreeWidgetに再現
        # の前に、Unitypackageを作成
        for k, v in self._gets(json_obj, ["rules", "includes_blacklist"], dict, {}).items():
            upkg = Unitypackage.createFromJsonDict({k: v})
            self.__addUnitypackage(self.ui.IncludesBlacklist_tw, upkg)

        for rule in self._gets(json_obj, ["rules", "file_blacklist"], list, []):
            itm: QListWidgetItem = QListWidgetItem(self.ui.FileBlacklist_list)
            itm.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled |
                         QtCore.Qt.ItemFlag.ItemIsEditable |
                         QtCore.Qt.ItemFlag.ItemIsSelectable)
            itm.setText(rule)

        for k, v in self._gets(json_obj, ["rules", "modifiable_assets"], dict, {}).items():
            upkg = Unitypackage.createFromJsonDict({k: v})
            self.__addUnitypackage(self.ui.ModifiableAsset_tw, upkg)

        for k, v in self._gets(json_obj, ["rules", "common_assets"], dict, {}).items():
            upkg = Unitypackage.createFromJsonDict({k: v})
            self.__addUnitypackage(self.ui.CommonAsset_tw, upkg)

        for rule in self._gets(json_obj, ["rules", "builtin_cgincludes"], list, []):
            itm: QListWidgetItem = QListWidgetItem(self.ui.BuiltinCGIncludes_list)
            itm.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled |
                         QtCore.Qt.ItemFlag.ItemIsEditable |
                         QtCore.Qt.ItemFlag.ItemIsSelectable)
            itm.setText(rule)
