import os
from datetime import datetime
from typing import Dict
import logging
import json

from ..common.data import Asset, Unitypackage


class Rule:
    __logger = logging.getLogger('Rule')

    def __init__(self):
        self.author: str = 'No name'
        self.__whitelist: Dict[str, Asset] = {}
        self.__blacklist: Dict[str, Asset] = {}

    def addWhitelistReference(self, asset: Asset):
        self.__whitelist[asset.guid] = asset

    def addBlacklistIncluded(self, asset: Asset):
        self.__blacklist[asset.guid] = asset

    def addWhitelistReferenceFromUnitypackage(self, unitypackage: Unitypackage):
        for asset in unitypackage.assets:
            self.addWhitelistReference(asset)

    def addBlacklistIncludedFromUnitypackage(self, unitypackage: Unitypackage):
        for asset in unitypackage.assets:
            self.addBlacklistIncluded(asset)

    def dumpToJson(self, dst: str) -> bool:
        if not dst:
            Rule.__logger.fatal('Output filepath is empty.')
            return False

        jdict: dict = {
            'header': {
                'author': self.author,
                'datetime': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            },
            'whitelist_reference': {},
            'blacklist_included': {}
        }

        for wasset in self.__whitelist.values():
            jdict['whitelist_reference'][wasset.guid] = wasset.toDict(False)

        for basset in self.__blacklist.values():
            jdict['whitelist_reference'][basset.guid] = basset.toDict(False)

        with open(os.path.join(os.getcwd(), dst), mode='w', encoding='utf-8') as fjson:
            json.dump(jdict, fjson, indent=4)
        return True


def batch_main(args):
    rule = Rule()
    rule.author = args.author
    for upack in args.import_packages:
        unitypackage = Unitypackage(package_filename=os.path.join(os.getcwd(), upack))
        unitypackage.loadFromUnitypackage()
        # TODO 今はテストで全部ホワイトリストに突っ込んでる
        rule.addWhitelistReferenceFromUnitypackage(unitypackage)
    rule.dumpToJson(args.output)
