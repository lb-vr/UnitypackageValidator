import logging

from typing import Dict, Tuple, List
from .validator_base import ValidatorBase
from unitypackage import Unitypackage, Asset, AssetType


class ModifiableAsset(ValidatorBase):
    __logger = logging.getLogger("ModifiableAsset")

    def __init__(self, unitypackage, rule):
        super().__init__("modifiable_assets", unitypackage, rule)

    def doIt(self) -> bool:
        self.logger.info("Validating ModifiableAsset.")

        modified_list: Dict[str, Dict[str, Tuple[dict, Asset]]] = {}

        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            for upkg_name, upkg in self.rule.items():
                if asset.guid in upkg.keys():
                    self.logger.debug("- Found same modifiable asset guid asset. Asset is %s", asset)
                    if upkg_name not in modified_list:
                        modified_list[upkg_name] = {}

                    modified_list[upkg_name][asset.guid] = (upkg[asset.guid], asset)
            else:
                self.logger.debug("[ O K ] %s", asset)

        # 改変・非改変をチェック
        for upkg_name, assets_pair in modified_list.items():
            modified = False
            self.logger.debug("Is modifing : Unitypackage = %s", upkg_name)
            for guid, itm in assets_pair.items():
                if itm[0]["hash"] != itm[1].hash:
                    self.logger.debug("- Found modified asset. %s", itm[1])
                    modified = True

            if modified:
                # 改変済み
                for _, itm in assets_pair.items():
                    ast: Asset = itm[1]
                    if ast.filetype == AssetType.kTexture or ast.filetype == AssetType.kHdrTexture:
                        # 改変されていなければ削除する
                        if itm[0]["hash"] == ast.hash:
                            # 削除
                            ast.delete()
                            self.appendLog("改変可能な共通アセットで、未改変なTextureが存在したため、削除しました。", itm[1])
                            self.logger.warning("[ FIX ] Deleted TEXTURE because of no modified. %s", itm[1])
                    # if ast.filetype == AssetType.kShader:
                        # シェーダーのインクルード検索処理
                        # self.checkShaderIncludes(ast)
                pass
            else:
                # 未改変
                # 全て消す
                for _, itm in assets_pair.items():
                    itm[1].delete()
                    self.appendLog("改変可能な共通アセットで、未改変なunitypackageが存在したため、削除しました。", itm[1])
                    self.logger.warning("[ FIX ] Deleted asset because of no modified. %s", itm[1])

        return True
