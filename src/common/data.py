import os
import enum
import re

from typing import Dict, Any


class AssetType(enum.Enum):
    kTexture = ('png', 'jpg', 'jpeg', 'bmp')
    kHdrTexture = ('exr', 'hdr', 'tif', 'tiff')
    kScene = ('unity',)
    kShader = ('shader', 'cginc')
    kMaterial = ('mat',)
    kDir = ('',)
    kUnknown = ('*',)

    @classmethod
    def getFromFilename(cls, fname: str):
        """
        ファイル名からアセットの種類を解析し、AssetTypeの列挙メンバを返す。
        """
        _, ext = os.path.splitext(os.path.basename(fname))
        ext = ext.lower().replace('.', '')
        for item in AssetType.__members__.values():
            if ext in item.value:
                return item
        return cls.kUnknown


class Asset:
    def __init__(self):
        self.__path: str = ''
        self.__type: AssetType = AssetType.kUnknown
        self.__guid: str = ''
        self.__reference_guids: Dict[str, Any] = {}

    def load(self, dir: str) -> str:
        """
        unitypackageからアセットの情報を取得します。
        unitypackageを解凍した後、guidで区切られたアセットフォルダに対して解析を行います。
        """
        with open(os.path.join(dir, 'pathname')) as fp:
            self.__path = fp.read()
        self.__type = AssetType.getFromFilename(self.__path)
        self.__guid = os.path.basename(dir)

        list1 = Asset.__getGuid(os.path.join(dir, 'asset.meta'))
        list2 = Asset.__getGuid(os.path.join(dir, 'asset'))
        list1.update(list2)
        list1.pop(self.__guid)
        self.__reference_guids = list1
        return self.__guid

    @property
    def path(self) -> str: return self.__path

    @property
    def assetType(self) -> AssetType: return self.__type

    @property
    def guid(self) -> str: return self.__guid

    def getReference(self) -> Dict[str, Any]: return self.__reference_guids

    def toDict(self, reference_info_include: bool = True) -> Dict[str, Any]:
        ret: Dict[str, Any] = {
            'guid': self.guid,
            'path': self.path,
            'type': self.assetType.name
        }
        if reference_info_include:
            reference_dict: Dict[str, Any] = {}
            for k, v in self.__reference_guids.items():
                if v:
                    reference_dict[k] = v.toDict(False)
                else:
                    reference_dict[k] = None
            ret['references'] = reference_dict
        return ret

    @classmethod
    def __getGuid(self, filepath: str) -> Dict[str, None]:
        matched: Dict[str, None] = {}
        try:
            fstr = ''
            with open(filepath, 'rt') as f:
                fstr = f.read()
            matched_list = re.findall(r'guid: [0-9a-f]{32}', fstr)
            for m in matched_list:
                matched[m[6:]] = None
        except UnicodeDecodeError:
            pass
        except FileNotFoundError:
            pass
        return matched
