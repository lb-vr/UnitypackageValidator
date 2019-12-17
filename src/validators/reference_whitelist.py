import re
import logging

from .validator_base import ValidatorBase
from unitypackage import Unitypackage


class ReferenceWhitelist(ValidatorBase):

    def __init__(self, unitypackage: Unitypackage, rule: dict):
        super().__init__("common_assets", unitypackage, rule)

    def doIt(self) -> bool:
        ret = True
        self.logger.info("Checking reference whitelist.")
        default_asset_regex_rule = re.compile(r"0000000000000000[0-9a-f]000000000000000")

        for asset in self.unitypackage.assets.values():
            for ref in asset.references:
                self.logger.debug("- Looking for reference asset. GUID is %s", ref)
                if ref in self.unitypackage.assets.keys():
                    # Self reference
                    self.logger.debug("- Found. Asset = %s", self.unitypackage.assets[ref].path)
                    continue

                if default_asset_regex_rule.match(ref):
                    self.logger.debug("- This is default asset.")
                    continue

                is_found: bool = False
                for upkg_name, upkg in self.rule.items():
                    if ref in upkg.keys():
                        is_found = True
                        self.logger.debug("- Found. Asset = <%s> %s (%s)", upkg_name, upkg[ref]["path"], ref)
                        break
                if is_found:
                    continue

                self.appendLog("参照可能でない外部アセットを参照しているため、エラーと判断されました。", asset)
                self.setFatalError()
                self.logger.warning("Reference Error. %s refers %s", asset.path, ref)
                ret = False

        return ret
