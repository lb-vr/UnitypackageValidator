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
