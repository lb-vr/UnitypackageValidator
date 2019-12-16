import logging
import os
import fnmatch

from .validator_base import ValidatorBase


class FilenameBlacklist(ValidatorBase):
    __logger = logging.getLogger("FilenameBlacklist")

    def __init__(self, unitypackage, rule):
        super().__init__("file_blacklist", unitypackage, rule)

    def doIt(self) -> bool:
        self.logger.info("Validating FilenameBlacklist.")
        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            filename = os.path.basename(asset.path)
            for r in self.rule:
                if fnmatch.fnmatch(filename, r):
                    asset.delete()
                    self.appendLog("同梱不可なファイルが含まれていたので、削除しました。", asset)
                    FilenameBlacklist.__logger.warning(
                        "[ FIX ] Included blackfile and removed. Asset is {0.guid} ({0.path})".format(asset))
                    break
            else:
                self.logger.debug("[ O K ] %s", asset)
        return True
