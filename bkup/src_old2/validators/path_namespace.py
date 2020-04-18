import logging
import re

from unitypackage import AssetType, Asset, Unitypackage


class PathNamespace:
    __logger = logging.getLogger("PathNamespace")

    def __init__(self, unitypackage, namespace: str):
        self.__unitypackage: Unitypackage = unitypackage
        self.__namespace: str = namespace
        self.__logger = PathNamespace.__logger

    def run(self) -> bool:
        self.__logger.info("Modifing PathNamespace.")
        for asset in self.__unitypackage.assets.values():
            if asset.deleted:
                continue

            self.modify(asset)
            self.__logger.debug("[ FIX ] Modified %s", asset)

        return True

    def modify(self, target_asset: Asset, encoding: str = "utf-8") -> bool:
        try:
            path: str = ""
            with open(target_asset.path_fpath, mode="r", encoding=encoding) as sf:
                path = re.sub(r'Assets/(.+)', r'Assets/{}/\1'.format(self.__namespace), sf.read(), 1)

            with open(target_asset.path_fpath, mode="w", encoding=encoding) as sf:
                sf.write(path)

            target_asset.updatePath()

        except UnicodeDecodeError:
            if encoding == "utf-8":
                self.__logger.warning("This shader is not utf-8 OMG. %s", target_asset)
                return self.modify(target_asset, "sjis")
            else:
                self.__logger.warning("This shader is not shift-jis too, WTF!? %s", target_asset)
                return False

        return True
