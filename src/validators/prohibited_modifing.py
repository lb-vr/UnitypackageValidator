import logging

from .validator_base import ValidatorBase


class ProhibitedModifing(ValidatorBase):
    __logger = logging.getLogger("ProhibitedModifing")

    def __init__(self, unitypackage, rule):
        super().__init__(unitypackage, rule)

    def doIt(self) -> bool:

        # 改変されていようが、されていまいが、確定で削除するもの
        # = 改変許可リストに乗っていないもの
        # パスまで見るか
        for asset in self.unitypackage.assets.values():
            for prohibited_modifing_guid, prohibited_modifing_asset in self.rule["prohibited_modifing"].items():
                if asset.guid == prohibited_modifing_guid \
                        and asset.path.split("/")[:-1] == prohibited_modifing_asset["path"].split("/")[:-1]:

                    ProhibitedModifing.warning(
                        "Delete prohibited modifing asset. Asset is %s (%s)", asset.guid, asset.path)
                    self.appendLog("改変が禁止されているアセットとして削除されました。", asset)
                    asset.delete()
                else:
                    self.appendNotice("改変が禁止されているアセットとGUIDが一致しましたが、パスが不一致だったため保留にしました。", asset)

        return True
