import logging
import os
import re

from typing import List
from unitypackage import Unitypackage


class ModifyRootDirectory:
    __logger = logging.getLogger("ModifyRootDirectory")

    def __init__(self, unitypackage: Unitypackage, user_id: str):
        self.__unitypackage: Unitypackage = unitypackage
        self.__user_id: str = user_id

    @property
    def logger(self) -> logging.Logger:
        return ModifyRootDirectory.__logger

    @property
    def unitypackage(self) -> Unitypackage:
        return self.__unitypackage

    def run(self) -> bool:
        self.logger.info("Modifing root directory.")

        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            new_path = "Assets/{}/{}".format(self.__user_id, asset.path[7:])
            with open(asset.path_fpath, mode="w", encoding="utf-8") as f:
                f.write(new_path)

            self.logger.debug("Modified root directory. %s", new_path)

        return True
