from .validator_base import ValidatorBase

from typing import List
from unitypackage import Unitypackage


class IncludesBlacklist(ValidatorBase):
    def __init__(self, unitypackage: Unitypackage, rule: dict):
        super().__init__("includes_blacklist", unitypackage, rule)

    def doIt(self) -> bool:
        self.logger.info("Validating IncludesBlacklist.")
        for asset in self.unitypackage.assets.values():
            if asset.deleted:
                continue

            for upkg in self.rule.values():
                if asset.guid in upkg.keys():
                    self.logger.debug("- Found same blacklisted guid asset. Asset is %s", asset)

                    # ルール上のパス名
                    rule_path = upkg[asset.guid]["path"]
                    self.logger.debug("|-- The path of rule asset is %s", rule_path)

                    # ルートを動かしていても無駄よ、という抵抗
                    rule_path = rule_path[7:]  # Assets/ を抜く

                    # チェック
                    if rule_path in asset.path:
                        asset.delete()
                        self.appendLog("同梱不可のアセットを削除しました。", asset)
                        self.logger.warning("* Deleted asset due to IncludedBlacklist. Asset is %s", asset)
                    else:
                        self.appendNotice("同梱不可のアセットと同じGUIDが見つかりましたが、パスが不一致なため保留されました。", asset)
                        self.logger.debug("|-- No action because test asset and rule asset are different asset path.")

        return True

        def createRule(self, unitypackages: List[Unitypackage]) -> dict:
            # ハッシュは使用しない
            return self.createRuleFromUnitypackage(unitypackages, False)
