import logging
import re
import os

from .validator_base import ValidatorBase


class FilenameBlacklist(ValidatorBase):
    __logger = logging.getLogger("FilenameBlacklist")

    def __init__(self, unitypackage, rule):
        super().__init__("filename_blacklist", unitypackage, rule)

    def doIt(self) -> bool:
        regex_rules: list = []

        for rrs in self.rule:
            regex_rules.append(re.compile(rrs))

        for asset in self.unitypackage.assets.values():
            filename = os.path.basename(asset.path)
            for rr in regex_rules:
                if rr.match(filename):
                    self.appendLog("同梱不可なファイルが含まれていたので、削除しました。", asset)
                    FilenameBlacklist.__logger.warning(
                        "- Included blackfile and removed. Asset is {0.guid} ({0.path})".format(asset))
                    break
        return True
