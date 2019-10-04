import tempfile
import tarfile
import logging
import os
import enum
import re

from typing import Dict, Any, List


class AssetType(enum.Enum):
    kTexture = ('png', 'jpg', 'jpeg', 'bmp')
    kHdrTexture = ('exr', 'hdr', 'tif', 'tiff')
    kScene = ('unity',)
    kShader = ('shader', 'cginc')
    kMaterial = ('mat',)
    kModel = ('fbx', 'obj')
    kAnimation = ('anim', 'controller')
    kPrefab = ('prefab',)
    kScript = ('cs',)

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
    __logger = logging.getLogger('Asset')

    def __init__(self):
        self.__path: str = ''
        self.__type: AssetType = AssetType.kUnknown
        self.__guid: str = ''
        self.__reference_guids: Dict[str, Any] = {}

    def load(self, dir: str, load_references: bool = True) -> str:
        """
        unitypackageからアセットの情報を取得します。
        unitypackageを解凍した後、guidで区切られたアセットフォルダに対して解析を行います。
        """
        with open(os.path.join(dir, 'pathname')) as fp:
            self.__path = fp.read()
        self.__type = AssetType.getFromFilename(self.__path)
        self.__guid = os.path.basename(dir)

        if load_references:
            list1 = Asset.__getGuid(os.path.join(dir, 'asset.meta'))
            list2 = Asset.__getGuid(os.path.join(dir, 'asset'))
            list1.update(list2)
            if self.__guid in list1:
                list1.pop(self.__guid)
            else:
                Asset.__logger.warning('there is no own guid in asset.meta. guid = %s, path = %s',
                                       self.guid, self.path)
            self.__reference_guids = list1
        return self.__guid

    @property
    def path(self) -> str:
        return self.__path

    @property
    def assetType(self) -> AssetType:
        return self.__type

    @property
    def guid(self) -> str:
        return self.__guid

    @property
    def references(self) -> Dict[str, Any]:
        return self.__reference_guids

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


class Unitypackage:
    __logger = logging.getLogger('Unitypackage')

    def __init__(self, package_filename: str, assets: List[Asset] = []):
        self.__package_filename: str = package_filename
        self.__assets: Dict[str, Asset] = {}
        for asset in assets:
            self.__assets[asset.guid] = asset
        self.__logger = Unitypackage.__logger

    @property
    def filename(self) -> str:
        return self.__package_filename

    @property
    def assets(self) -> Dict[str, Asset]:
        return self.__assets

    def loadFromUnitypackage(self) -> bool:
        ret = True
        self.__logger.info('Start to load %s package.', self.__package_filename)
        cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            self.__logger.debug(' - Working dir = %s', tmpdir)
            # open tar
            try:
                with tarfile.open(self.__package_filename, 'r:gz') as tar:
                    self.__logger.debug(' - %d file(s) are included.', len(tar.getnames()))

                    # extract tar
                    tar.extractall()
                    folders = os.listdir()
                    self.__logger.debug(' - Extracted.')

                    for f in folders:
                        asset = Asset()
                        asset.load(f)
                        self.__assets[asset.guid] = asset

            except FileNotFoundError:
                self.__logger.error(' - Unitypackage is not found. PATH = "%s"', self.__package_filename)
                ret = False
            finally:
                os.chdir(cwd)
        return ret

    def linkReferences(self, whitelist: Dict[str, Asset] = {}):
        for asset in self.__assets.values():
            # asset loop
            references = asset.references
            for ref_guid in references.keys():
                # reference loop
                if ref_guid in self.__assets:
                    self.__logger.debug('Find Referenced Asset! %s', ref_guid)
                    # self.__assets[asset.guid].references[ref_guid] = self.__assets[ref_guid]  # linking
                    asset.references[ref_guid] = self.__assets[ref_guid]
                elif ref_guid in whitelist:
                    asset.references[ref_guid] = whitelist[ref_guid]  # linking to whitelist

    def toDict(self) -> dict:
        assets = {}
        for asset in self.__assets.values():
            assets[asset.guid] = asset.toDict()

        ret = {
            'filename': self.__package_filename,
            'assets': assets
        }
        return ret
