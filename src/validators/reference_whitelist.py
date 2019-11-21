import re
import logging

from .validator_base import ValidatorBase
from ..unitypackage import Unitypackage


class ReferenceWhitelist(ValidatorBase):
    __logger = logging.getLogger("ReferenceWhitelist")

    def __init__(self, unitypackage: Unitypackage, rule: dict):
        super().__init__(unitypackage, rule)

    def doIt(self) -> bool:
        ret = True
        ReferenceWhitelist.__logger.info("Checking reference whitelist.")
        default_asset_regex_rule = re.compile(r"0000000000000000[0-9a-f]000000000000000")

        for asset in self.unitypackage.assets.values():
            for ref in asset.references:
                ReferenceWhitelist.__logger.debug("- Looking for reference asset. GUID is %s", ref)
                if ref in self.unitypackage.assets.keys():
                    # Self reference
                    ReferenceWhitelist.__logger.debug("- Found. Asset = %s", self.unitypackage.assets[ref].path)
                    continue

                if default_asset_regex_rule.match(ref):
                    ReferenceWhitelist.__logger.debug("- This is default asset.")
                    continue

                is_found: bool = False
                for upkg in self.rule["reference_whitelist"].values():
                    if ref in upkg.keys():
                        is_found = True
                        ReferenceWhitelist.__logger.debug("- Found. Asset = %s", upkg[ref].path)
                        break
                if is_found:
                    continue

                self.appendLog("参照可能でない外部アセットを参照しているため、エラーと判断されました。", asset)
                ReferenceWhitelist.__logger.warning("Reference Error. %s refers %s", asset.path, ref)
                ret = False

        return ret
