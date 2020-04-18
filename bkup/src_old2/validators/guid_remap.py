import logging
import re
from typing import List
from unitypackage import AssetType, Asset, Unitypackage


class GuidRemap:
    __logger = logging.getLogger("GuidRemap")

    def __init__(self, unitypackage, namespace: str):
        self.__unitypackage: Unitypackage = unitypackage
        self.__logger = GuidRemap.__logger

    def run(self) -> bool:
        self.__logger.info("Remapping GUID")
        for asset in self.__unitypackage.assets.values():
            if asset.deleted:
                continue

            if asset.filetype != AssetType.kShader:
                continue

            before_guid = asset.guid
            asset.updateGuid()
            self.__logger.debug("[ FIX ] GUID Remapped, %s -> %s", before_guid, asset.guid)

        # 衝突していないか確認
        new_guid_list: List[str] = [g.guid for g in self.__unitypackage.assets.values() if g.deleted is not False]
        if len(list(set(new_guid_list))) != len(new_guid_list):
            self.__logger.warning("[WARNING] Renewed GUID Collided.")
            return self.run()  # Retry.

        return True
