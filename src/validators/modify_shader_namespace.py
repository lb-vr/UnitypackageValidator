import logging
import re

from typing import List
from unitypackage import Unitypackage


class ModifyShaderNamespace:
    __logger = logging.getLogger("ModifyShaderNamespace")

    def __init__(self, unitypackage: Unitypackage, user_id: str):
        self.__unitypackage: Unitypackage = unitypackage
        self.__log: List[str] = []
        self.__user_id: str = user_id

    @property
    def logger(self) -> logging.Logger:
        return ModifyShaderNamespace.__logger

    def getLog(self) -> List[str]:
        return self.__log

    @property
    def unitypackage(self) -> Unitypackage:
        return self.__unitypackage

    def run(self) -> bool:
        self.logger.info("Modifing shader namespace")

        regex_pattern = re.compile(r'Shader\s+"([^"]+)"')

        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            if asset.path.endswith(".shader"):
                # シェーダーファイル
                shader_code = ""
                with open(asset.data_fpath, mode="r", encoding="utf-8") as f:
                    shader_code = f.read()

                shader_code = regex_pattern.sub('Shader "{}/\\1"'.format(self.__user_id), shader_code)

                with open(asset.data_fpath, mode="w", encoding="utf-8") as f:
                    f.write(shader_code)

                self.logger.debug("Modified shader namespace. %s", asset)

        return True
