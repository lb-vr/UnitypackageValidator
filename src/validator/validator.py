from typing import Dict
import logging
import os
import tempfile
import tarfile
import enum
import json


class AssetType(enum.Enum):
    kTexture = ('png', 'jpg', 'jpeg', 'bmp', 'hdr', 'tif')
    kScene = ('scene',)
    kShader = ('shader', 'cginc')
    kMaterial = ('mat',)
    kDir = ('',)
    kUnknown = ('*',)

    @classmethod
    def getFromFilename(cls, fname: str):
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

    def load(self, dir: str) -> str:
        with open(os.path.join(dir, 'pathname')) as fp:
            self.__path = fp.read()
        self.__type = AssetType.getFromFilename(self.__path)
        self.__guid = os.path.basename(dir)
        return self.__guid

    @property
    def path(self) -> str: return self.__path

    @property
    def assetType(self) -> AssetType: return self.__type

    @property
    def guid(self) -> str: return self.__guid

    def toDict(self) -> dict:
        ret = {
            'guid': self.guid,
            'path': self.path,
            'type': self.assetType.name
        }
        return ret


class Validator:
    __logger = logging.getLogger('Validator')

    def __init__(self):
        self.__assets: Dict[str, Asset] = {}
        self.__logger = Validator.__logger

    def loadUnitypackage(self, upkg: str):
        cwd = os.getcwd()
        self.__logger.debug('Start to validate. Package = %s', upkg)
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            self.__logger.debug(' - Working dir = %s', tmpdir)
            # open tar
            with tarfile.open(upkg, 'r:gz') as tar:
                self.__logger.debug(' - %d file(s) are included.', len(tar.getnames()))
                tar.extractall()
                folders = os.listdir()
                for f in folders:
                    asset = Asset()
                    guid = asset.load(f)
                    self.__assets[guid] = asset
            os.chdir(cwd)

    def dumpToJson(self, dst: str):
        ret = {}
        for k, v in self.__assets.items():
            ret[k] = v.toDict()

        with open(os.path.join(os.getcwd(), dst), mode='w', encoding='utf-8') as fjson:
            json.dump(ret, fjson, indent=4)


def batch_main(args):
    for pkg in args.packages:
        vd = Validator()
        vd.loadUnitypackage(os.path.join(os.getcwd(), pkg))
        vd.dumpToJson(os.path.join(os.getcwd(), os.path.basename(pkg) + '-' + args.output))
