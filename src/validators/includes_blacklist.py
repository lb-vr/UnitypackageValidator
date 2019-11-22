import logging

from .validator_base import ValidatorBase


class IncludesBlacklist(ValidatorBase):
    __logger = logging.getLogger("IncludesBlacklist")

    def __init__(self, unitypackage, rule):
        super().__init__("includes_blacklist", unitypackage, rule)

    def doIt(self) -> bool:
        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            for upkg in self.rule.values():
                if asset.guid in upkg.keys():
                    rule_path = upkg[asset.guid]["path"][7:]  # Assets/ を抜く
                    if rule_path in asset.path:
                        asset.delete()
                        self.appendLog("同梱不可のアセットを削除しました。", asset)
                    else:
                        self.appendNotice("同梱不可のアセットと同じGUIDが見つかりましたが、パスが不一致なため保留されました。")

        return True
