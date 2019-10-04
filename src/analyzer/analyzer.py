# (c) 2019 lb-vr (WhiteAtelier)
import os

import json
import logging

from typing import List

from ..rule.rule import Rule
from ..common.data import Asset, AssetType, Unitypackage


class AssetReferenceError:
    def __init__(self, asset: Asset, missing: str):
        self.__asset: Asset = asset
        self.__missing: str = missing


class Analyzer:
    __logger = logging.getLogger('Analyzer')

    def __init__(self, unitypackage: Unitypackage):
        self.__unitypackage: Unitypackage = unitypackage
        self.__logger = Analyzer.__logger

    def analyzeReference(self, rule: Rule) -> List[AssetReferenceError]:
        ret: List[AssetReferenceError] = []

        for val in self.__unitypackage.assets:
            guids = list(val.getReference().keys())
            for k in guids:
                if k in self.__unitypackage.assets.keys():
                    val.getReference()[k] = self.__unitypackage.assets[k]
                    continue
                # elif rule.searchGuid(req):
                #    continue
                else:
                    ret.append(AssetReferenceError(val, k))
                    self.__logger.warning('AssetReferenceError : %s -> %s', val.path, k)
        return ret

    def dumpToJson(self, dst: str):
        ret = {}
        for asset in self.__unitypackage.assets:
            ret[asset.guid] = asset.toDict()

        with open(os.path.join(os.getcwd(), dst), mode='w', encoding='utf-8') as fjson:
            json.dump(ret, fjson, indent=4)


def batch_main(args):
    for pkg in args.import_packages:
        unitypackage = Unitypackage(os.path.join(os.getcwd(), pkg))
        if not unitypackage.loadFromUnitypackage():
            exit(-1)

        unitypackage.linkReferences({})

    ret = unitypackage.toDict()
    with open(os.path.join(os.getcwd(), args.output), mode='w', encoding='utf-8') as fjson:
        json.dump(ret, fjson, indent=4)
