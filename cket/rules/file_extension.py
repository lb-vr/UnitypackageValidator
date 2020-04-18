from typing import List
from srolib.unity.unitypackage import Unitypackage
from cket import exceptions
from .base import BaseRule, Result
from srolib.util import easy_logger


@easy_logger.easy_logging
class FileExtensionRule(BaseRule):

    def __init__(self, exts: list, list_type: str):
        super().__init__()
        exceptions.InvalidRuleError.assertion(type(exts) is list)
        exceptions.InvalidRuleError.assertion(type(list_type) is str)
        exceptions.InvalidRuleError.assertion(list_type in ["blacklist", "whitelist"])
        for ext in exts:
            exceptions.InvalidRuleError.assertion(type(ext) is str)

        self.exts: List[str] = exts
        self.list_type: str = list_type

    def run(self, upkg: Unitypackage, **kwargs) -> Result:
        result: Result = Result(self)
        for name, asset in upkg.assets.items():
            if (asset.filetype in self.exts and self.list_type == "blacklist") or\
                    (asset.filetype not in self.exts and self.list_type == "whitelist"):

                asset.delete()
                result.reportSuccess(asset, "Deleted")
        return result

    @classmethod
    def jsonKey(cls) -> str:
        return "file_ext"
