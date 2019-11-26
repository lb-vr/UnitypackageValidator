import logging
import os

from typing import List
from unitypackage import Unitypackage, AssetType


class FloatingAsset:
    __logger = logging.getLogger("FloatingAsset")

    def __init__(self, unitypackage: Unitypackage):
        self.__unitypackage: Unitypackage = unitypackage
        self.__log: List[str] = []

    @property
    def logger(self) -> logging.Logger:
        return FloatingAsset.__logger

    def getLog(self) -> List[str]:
        return self.__log

    @property
    def unitypackage(self) -> Unitypackage:
        return self.__unitypackage

    def run(self) -> bool:
        self.logger.info("Deleting FloatingAsset.")
        reference_list: List[str] = []
        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            reference_list += asset.references

        # 重複削除
        reference_list = list(set(reference_list))

        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            if asset.guid in reference_list:
                # 参照されていない
                # とりあえずテクスチャは削除していいかな
                if asset.filetype == AssetType.kTexture or \
                        asset.filetype == AssetType.kHdrTexture:
                    self.logger.warning("Delete asset which is not referenced. %s", asset)
                    self.__log.append("テクスチャで、かつ何からも参照されていないため削除されました")
                    asset.delete()

        return True
