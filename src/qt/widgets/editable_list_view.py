import dataclasses
from typing import List
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QListView
)
from PySide2.QtCore import QAbstractListModel, Qt, QModelIndex


class _InternalData:
    def __init__(self, instance, getter="__str__", setter=""):
        self.__getter = getattr(instance.__class__, getter) if getter else instance.__class__.__str__
        self.__setter = getattr(instance.__class__, setter) if setter else None
        self.__data = instance

    def getVal(self):
        return self.__getter(self.__data)

    @property
    def data(self):
        return self.__data

    def __eq__(self, other):
        return self.getVal() == other.getVal()

    def setVal(self, value):
        if self.__setter:
            return self.__setter(self.__data, value)
        self.__data = self.__data.__class__(value)
        return True


class EditableListModel(QAbstractListModel):
    def __init__(self,
                 addable: bool,
                 removable: bool,
                 swappable: bool,
                 editable: bool,
                 base_dataclass=str,
                 getter="__str__",
                 setter="",  # 空文字で直接代入
                 parent=None):
        super().__init__(parent)
        self.__data: list = []
        self.__base_dataclass = base_dataclass
        self.__addable: bool = addable
        self.__removable: bool = removable
        self.__editable: bool = editable
        self.__swappable: bool = swappable
        self.__getter: str = getter
        self.__setter: str = setter

    @property
    def internalData(self) -> list:
        return self.__data

    @property
    def addable(self) -> bool:
        return self.__addable

    @property
    def removable(self) -> bool:
        return self.__removable

    @property
    def editable(self) -> bool:
        return self.__editable

    @property
    def swappable(self) -> bool:
        return self.__swappable

    def rowCount(self, _):
        return len(self.__data)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.__data[index.row()].getVal()
        if role == Qt.UserRole:
            return self.__data[index.row()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return ""

    def setData(self, index: QModelIndex, value, role: int = Qt.EditRole):
        if role == Qt.EditRole:
            return self.__data[index.row()].setVal(value)

    def flags(self, index: QModelIndex):
        ret = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if self.__editable:
            ret |= Qt.ItemIsEditable
        return ret

    def append(self, *args, **kwarg):
        if self.__addable is False:
            return

        new_data = _InternalData(self.__base_dataclass(*args, **kwarg), self.__getter, self.__setter)
        if self.__data:
            if new_data == self.__data[-1]:
                return

        self.beginInsertRows(QModelIndex(), len(self.__data), len(self.__data) + 1)
        self.__data.append(new_data)
        self.endInsertRows()

    def remove(self, row_index: int):
        if row_index < len(self.__data):
            self.beginRemoveRows(QModelIndex(), row_index, row_index)
            self.__data.pop(row_index)
            self.endRemoveRows()


class EditableListView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__layout: QVBoxLayout = QVBoxLayout()
        self.__list_view: QListView = QListView()
        self.__button_layout: QHBoxLayout = QHBoxLayout()
        self.__add_button: QToolButton = QToolButton()
        self.__upward_button: QToolButton = QToolButton()
        self.__downward_button: QToolButton = QToolButton()
        self.__remove_button: QToolButton = QToolButton()

        self.__add_button.setText("+")
        self.__add_button.clicked.connect(self.__e_add)
        self.__upward_button.setText("↑")
        self.__downward_button.setText("↓")
        self.__remove_button.setText("-")
        self.__remove_button.clicked.connect(self.__e_remove)

        self.__button_layout.addWidget(self.__add_button)
        self.__button_layout.addWidget(self.__upward_button)
        self.__button_layout.addWidget(self.__downward_button)
        self.__button_layout.addWidget(self.__remove_button)
        self.__button_layout.addStretch()

        self.__layout.addWidget(self.__list_view)
        self.__layout.addLayout(self.__button_layout)

        self.setLayout(self.__layout)

        self.__model: EditableListModel = None

        self.__add_args = []
        self.__add_kwargs = {}

    def setModel(self, model: EditableListModel):
        self.__add_button.setVisible(model.addable)
        self.__add_button.setEnabled(model.addable)
        self.__upward_button.setVisible(model.swappable)
        self.__upward_button.setEnabled(model.swappable)
        self.__downward_button.setVisible(model.swappable)
        self.__downward_button.setEnabled(model.swappable)
        self.__remove_button.setVisible(model.removable)
        self.__remove_button.setEnabled(model.removable)
        self.__model = model
        self.__list_view.setModel(model)

    def setAddArgs(self, *args, **kwargs):
        self.__add_args = args
        self.__add_kwargs = kwargs

    def getListData(self) -> list:
        if self.__model is None:
            return []
        return [f.data for f in self.__model.internalData]

    def appendItem(self, *args, **kwargs):
        self.__model.append(*args, **kwargs)

    def removeItem(self, row_index: int):
        self.__model.remove(row_index)

    def __e_add(self):
        self.appendItem(*self.__add_args, **self.__add_kwargs)

    def __e_remove(self):
        current_index = self.__list_view.selectedIndexes()
        if current_index:
            self.removeItem(current_index[0].row())
