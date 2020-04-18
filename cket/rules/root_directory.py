from typing import List
from srolib.unity.unitypackage import Unitypackage
from cket import exceptions
from . import BaseRule, Result
from srolib.util import easy_logger


@easy_logger.easy_logging
class RootDirectoryIDRule(BaseRule):

    def __init__(self, operation: str):
        super().__init__()
        exceptions.InvalidRuleError.assertion(type(operation) is str)
        exceptions.InvalidRuleError.assertion(operation in ["delete", "nest"])
        self.operation = operation

    def run(self, upkg: Unitypackage, eid: int, **kwargs) -> Result:
        result: Result = Result(self)
        for name, asset in upkg.assets.items():
            if asset.pathname.startswith(f"Assets/{eid}/"):
                # under eid directory
                continue
            elif asset.pathname == f"Assets/{eid}" and asset.hash is None:
                # directory
                continue
            else:
                if self.operation == "delete":
                    asset.delete()
                    result.reportSuccess(asset, "Deleted")
                else:
                    asset.move(f"Assets/{eid}/{asset.pathname[7:]}")
                    result.reportSuccess(asset, "Moved.")

        return result

    @classmethod
    def jsonKey(cls) -> str:
        return "root_directory_id"
