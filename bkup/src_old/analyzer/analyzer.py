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

    def toDict(self) -> dict:
        return {
            'error': 'AssetReferenceError',
            'asset': self.__asset.toDict(),
            'missing': self.__missing
        }


def batch_main(args):
    for pkg in args.import_packages:
        unitypackage = Unitypackage(os.path.join(os.getcwd(), pkg))
        if not unitypackage.loadFromUnitypackage():
            exit(-1)

        unitypackage.linkReferences({})

    ret = unitypackage.toDict()
    with open(os.path.join(os.getcwd(), args.output), mode='w', encoding='utf-8') as fjson:
        json.dump(ret, fjson, indent=4)
