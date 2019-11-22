import hashlib
import logging

from typing import Dict

from .validator_base import ValidatorBase
from unitypackage import Asset


class IncludeCommonAsset(ValidatorBase):
    __logger = logging.getLogger("IncludeCommonAsset")

    def __init__(self, unitypackage, rule):
        super().__init__(unitypackage, rule)

    def doIt(self) -> bool:
        same_pair: Dict[str, Dict[str, Asset]] = {}
        diff_pair: Dict[str, Dict[str, Asset]] = {}

        for asset in self.unitypackage.assets.values():
            for upkg_name, upkg in self.rule["include_common_asset"].items():
                if asset.guid in upkg.keys():
                    IncludeCommonAsset.__logger.info("Find common asset (same guid).")
                    # 含まれていた
                    # ハッシュを比較
                    test_hashbytes: str = ""
                    common_hashbytes: str = upkg[asset.guid]["hash"]
                    with open(asset.data_fpath, mode="rb") as asset_data_f:
                        test_hashbytes = hashlib.sha512(asset_data_f.read()).hexdigest()

                    IncludeCommonAsset.__logger.debug("- Test asset sha-512 hash = %s", test_hashbytes)
                    IncludeCommonAsset.__logger.debug("- Rule asset sha-512 hash = %s", common_hashbytes)

                    if upkg_name not in same_pair:
                        same_pair[upkg_name] = {}

                    if test_hashbytes == common_hashbytes:
                        # 完全に一致した

                        same_pair[upkg_name][asset.guid] = asset
                        IncludeCommonAsset.__logger.warning("Find common asset (same guid and file hash).")
                        break

                    # 改変済みだった
                    IncludeCommonAsset.__logger.info("- Modified.")
                    diff_pair[upkg_name][asset.guid] = asset

        # diff_pairに無く、same_pairにあるunitypackageを探す
        for upkg_name, guid_asset in same_pair.items():
            if upkg_name not in diff_pair.keys():
                # 全く一緒のunitypackageであるので、削除する
                for asset in guid_asset.values():
                    self.appendLog("改変可能な外部アセット群が全て未改変の状態で同梱されているため、削除します。", asset)
                    asset.delete()
            else:
                self.appendNotice(
                    "改変可能な外部アセット群に対し改変が加えられているため、削除しませんでした。unitypackage名は" + upkg_name + "です。")

        # shaderの階層掘り下げは、
        # 残ったアセット全てのシェーダーに対して行えばいい

        return True
