
import logging
from typing import List, Tuple
from srolib.unity.unitypackage import Asset


class Result:
    def __init__(self, rule):
        self.rule = rule
        self.__records: List[Tuple[int, Asset, str]] = []

    def __report(self, level: int, asset: Asset, message: str):
        self.__records.append((level, asset, message))

    def __getRecords(self, level: int) -> List[Tuple[int, Asset, str]]:
        ret = []
        for r in self.__records:
            if r[0] == level:
                ret.append(r)
        return ret

    def reportSuccess(self, asset: Asset, message: str):
        self.__report(0, asset, message)

    def reportWarning(self, asset: Asset, message: str):
        self.__report(1, asset, message)

    def reportError(self, asset: Asset, message: str):
        self.__report(2, asset, message)

    @property
    def success(self) -> List[Tuple[int, Asset, str]]:
        return self.__getRecords(0)

    @property
    def warning(self) -> List[Tuple[int, Asset, str]]:
        return self.__getRecords(1)

    @property
    def errors(self) -> List[Tuple[int, Asset, str]]:
        return self.__getRecords(2)

    def __str__(self) -> str:
        return (f"Result of {self.rule.rule_name} : "
                f"{len(self.success)} Success, "
                f"{len(self.warning)} Warning, "
                f"{len(self.errors)} Error(s).")

    def __repr__(self) -> str:
        ret = [self.__str__()]
        label = ["+ SUCCESS", "- WARNING", "!!! ERROR"]
        for r in self.__records:
            ret.append(f"{label[r[0]]} {r[1].filename} ... {r[2]}")
            ret.append(f"\tAsset = {r[1]}")
            ret.append("")
        return "\n".join(ret)


class BaseRule:
    def __init__(self):
        self.rule_name: str = self.__class__.__name__

    @staticmethod
    def getRuleInstances(rulelist: list):
        from . import _rule_all_classes
        logger = logging.getLogger()
        ret = []
        for drule in rulelist:
            for rule_class in _rule_all_classes:
                if rule_class.jsonKey() == drule["name"]:
                    logger.debug("add rule. Rule = %s, jsonKey = %s",
                                 rule_class.__name__,
                                 rule_class.jsonKey())
                    ret.append(rule_class(**{k: v for k, v in drule.items() if k != "name"}))
        return ret

    @classmethod
    def jsonKey(cls):
        raise NotImplementedError(cls.__name__)
