# (c) 2019 lb-vr (WhiteAtelier)
import os

import enum
import json
import logging
import re
import tarfile
import tempfile

from typing import Dict, List, Any

from ..rule.rule import Rule


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

    def toDict(self, reference_info_include: bool = True) -> dict:
        ret = {
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


class AssetReferenceError:
    def __init__(self, asset: Asset, missing: str):
        self.__asset: Asset = asset
        self.__missing: str = missing


class Analyzer:
    __logger = logging.getLogger('Analyzer')

    def __init__(self):
        self.__assets: Dict[str, Asset] = {}
        self.__logger = Analyzer.__logger

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

    def analyzeReference(self, rule: Rule) -> List[AssetReferenceError]:
        ret: List[AssetReferenceError] = []

        for val in self.__assets.values():
            guids = list(val.getReference().keys())
            for k in guids:
                if k in self.__assets.keys():
                    val.getReference()[k] = self.__assets[k]
                    continue
                # elif rule.searchGuid(req):
                #    continue
                else:
                    ret.append(AssetReferenceError(val, k))
                    self.__logger.warning('AssetReferenceError : %s -> %s', val.path, k)
        return ret

    def dumpToJson(self, dst: str):
        ret = {}
        for k, v in self.__assets.items():
            ret[k] = v.toDict()

        with open(os.path.join(os.getcwd(), dst), mode='w', encoding='utf-8') as fjson:
            json.dump(ret, fjson, indent=4)


def batch_main(args):
    for pkg in args.import_packages:
        analyzer = Analyzer()
        analyzer.loadUnitypackage(os.path.join(os.getcwd(), pkg))
        ret = analyzer.analyzeReference(None)
        analyzer.dumpToJson(os.path.join(os.getcwd(), os.path.basename(pkg) + '-' + args.output))
