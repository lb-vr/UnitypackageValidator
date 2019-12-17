import logging
import re
import os

from .validator_base import ValidatorBase

from unitypackage import AssetType, Asset
from typing import List


class ShaderIncludes(ValidatorBase):
    __logger = logging.getLogger("ShaderIncludes")

    def __init__(self, unitypackage, rules):
        super().__init__("builtin_cgincludes", unitypackage, rules)

    def doIt(self) -> bool:
        self.logger.info("Validating ShaderIncludes.")
        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            if asset.filetype != AssetType.kShader:
                continue

            if self.checkShaderIncludes(asset):
                self.logger.debug("[ O K ] %s", asset)

        return True

    def checkShaderIncludes(self, target_asset: Asset, encoding: str = "utf-8") -> bool:
        try:
            with open(target_asset.data_fpath, mode="r", encoding=encoding) as sf:
                self.__logger.debug("- Checking shader file. %s", target_asset)
                includes: List[str] = re.findall(r'#include "(?P<include_path>[^"]+)"', sf.read())
                dirnm: str = os.path.dirname(target_asset.path)
                for inc in includes:
                    self.__logger.debug("-- includes: %s", inc)

                    # 絶対パスか
                    if "Assets" in inc:
                        self.setFatalError()
                        self.appendLog("シェーダーincludeの絶対パスincludeは許可されません", target_asset)
                        self.__logger.warning("[FATAL] Absolute path is prohibited. %s", target_asset)

                    # インクルード先が含まれているか
                    p = os.path.normpath(os.path.join(dirnm, inc)).replace("\\", "/")
                    for aitm in self.unitypackage.assets.values():
                        if aitm.path == p:
                            self.__logger.debug("- Found required cginc file. %s includes %s.", target_asset.path, p)
                            break  # found
                    else:
                        # 埋め込みシェーダーかもしれない
                        if inc in self.rule:
                            self.__logger.debug(
                                "- Found required cginc file in built-in set. %s includes %s.", target_asset.path, p)
                        else:
                            # Not Found.
                            self.__logger.error(
                                "[FATAL] Required cginc file is not included in this unitypackage. %s", target_asset)
                            self.appendLog("shaderファイルからインクルードされているcgincファイルが見つかりませんでした", target_asset)
                            self.setFatalError()

        except UnicodeDecodeError:
            if encoding == "utf-8":
                self.appendNotice("このシェーダーファイルはutf-8として不正な文字が含まれていました。Shift-jisでリトライします。", target_asset)
                self.logger.warning("This shader is not utf-8 OMG. %s", target_asset)
                return self.checkShaderIncludes(target_asset, "sjis")
            else:
                self.appendNotice("このシェーダーファイルはエンコードエラーで読み取りができませんでした", target_asset)
                self.logger.warning("This shader is not shift-jis too, WTF!? %s", target_asset)
                return False

        return True
