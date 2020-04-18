import logging
import re

from unitypackage import AssetType, Asset, Unitypackage


class ShaderNamespace:
    __logger = logging.getLogger("ShaderNamespace")

    def __init__(self, unitypackage, namespace: str):
        self.__unitypackage: Unitypackage = unitypackage
        self.__namespace: str = namespace
        self.__logger = ShaderNamespace.__logger

    def run(self) -> bool:
        self.__logger.info("Modifing ShaderNamespace.")
        for asset in self.__unitypackage.assets.values():
            if asset.deleted:
                continue

            if asset.filetype != AssetType.kShader:
                continue

            self.modify(asset)
            asset.updateHash()
            self.__logger.debug("[ FIX ] Modified %s, hash is %s", asset, asset.hash)

        return True

    def modify(self, target_asset: Asset, encoding: str = "utf-8") -> bool:
        try:
            shader_body: str = ""
            with open(target_asset.data_fpath, mode="r", encoding=encoding) as sf:
                self.__logger.debug("- Checking shader file. %s", target_asset)
                shader_body = re.sub(r'Shader(\s+)"([^"]+)"',
                                     r'Shader\1"{}/\2"'.format(self.__namespace), sf.read(), 1)

            with open(target_asset.data_fpath, mode="w", encoding=encoding) as sf:
                sf.write(shader_body)

            with open(r"D:\test.shader", mode="w", encoding=encoding) as sf:
                sf.write(shader_body)

        except UnicodeDecodeError:
            if encoding == "utf-8":
                self.__logger.warning("This shader is not utf-8 OMG. %s", target_asset)
                return self.modify(target_asset, "sjis")
            else:
                self.__logger.warning("This shader is not shift-jis too, WTF!? %s", target_asset)
                return False

        return True
