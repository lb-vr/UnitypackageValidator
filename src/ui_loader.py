import dataclasses
from typing import Any
from PySide2.QtUiTools import QUiLoader

import qt.widgets


class UiLoaderWithRootWidget(QUiLoader):

    def __init__(self, root_widget):
        super().__init__()
        self.__root_widget = root_widget

    def createWidget(self, class_name, parent=None, name=''):
        if parent is None and self.__root_widget is not None:
            return self.__root_widget
        if hasattr(qt.widgets, class_name):
            ret = getattr(qt.widgets, class_name)(parent=parent)
            ret.setObjectName(name)
            return ret
        return super().createWidget(class_name, parent, name)


@dataclasses.dataclass(eq=False)
class UiContainer:
    """ UIをdataclassに展開するための基底クラス

    必ずこのクラスを継承したdataclassを定義し、ウィジット名のメンバを用意すること

    Attributes:
        widgets (Any):
            すべてのuiが格納されているfield
    """

    widgets: Any

    def __post_init__(self):
        if type(self) is UiContainer:
            raise RuntimeError("Do not create UiContainer instance."
                               "Inherit this class, and create its instance.")

    @classmethod
    def load(cls, filepath: str, uiLoader=UiLoaderWithRootWidget, *args, **kwargs):
        """ UIファイルからUIを読み込みdataclassに展開する

        Parameter:
            filepath (str):
                uiファイルパス
            uiLoader (class):
                カスタムで使用するUIローダー.
                デフォルトでmovtoolsのUIローダーが使用される.

        Returns:
            UiContainer:
                UIファイルから構築されたUiContainerの継承インスタンス.

        raise:
            FileNotFound:
                uiファイルが見つからない場合
            TypeError:  
                継承クラスに記述されたtypingアノテーションと、実際のUIの型が異なる場合
            KeyError:
                継承クラスに記述されたウィジットが、UIファイルに存在しない場合
        """
        ui = uiLoader(*args, **kwargs).load(filepath)

        kargs = {"widgets": ui}
        fields: dict = {f.name: f for f in dataclasses.fields(cls)}

        for fname, field in fields.items():
            if fname in ui.__dict__:
                v = ui.__dict__[fname]
                if field.type == type(v):
                    kargs[fname] = v
                else:
                    raise TypeError(f"UI '{fname}' was '{type(v)}', excepted '{field.type}'. {filepath}")
            elif fname not in ["widgets", "signaler"]:
                raise KeyError(f"UI '{fname}'(type='{field.type}') is not included. {filepath}")

        ret = cls(**kargs)
        return ret
