import abc
import logging

from typing import List, Optional
from unitypackage import Unitypackage, Asset


class ValidatorBase(metaclass=abc.ABCMeta):
    def __init__(self, rule_name: str, unitypackage: Unitypackage, rule):
        self.__unitypackage: Unitypackage = unitypackage
        self.__rule = rule
        self.__rule_name: str = rule_name
        self.__logs: List[str] = []
        self.__notices: List[str] = []
        self.__logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.__fatal: bool = False

    @property
    def unitypackage(self) -> Unitypackage:
        return self.__unitypackage

    @property
    def rule(self):
        if self.__rule:
            if "rules" in self.__rule:
                if self.rule_name in self.__rule["rules"]:
                    return self.__rule["rules"][self.rule_name]
        return None

    @property
    def rule_name(self) -> str:
        return self.__rule_name

    @property
    def logger(self) -> logging.Logger:
        return self.__logger

    @abc.abstractmethod
    def doIt(self) -> bool:
        pass

    def run(self) -> bool:
        # return self.doIt() if self.rule else True
        return self.doIt()

    def appendLog(self, message: str, asset: Optional[Asset] = None):
        self.__logs.append(message + self.__assetToMsg(asset))

    def appendNotice(self, message: str, asset: Optional[Asset] = None):
        self.__notices.append(message + self.__assetToMsg(asset))

    def getLog(self) -> List[str]:
        return self.__logs

    def getNotice(self) -> List[str]:
        return self.__notices

    @property
    def fatal(self) -> bool:
        return self.__fatal

    def setFatalError(self):
        self.__fatal = True

    """
    def createRuleFromUnitypackage(self, unitypackages: List[Unitypackage], with_hash: bool = False) -> dict:
        ret: dict = {self.rule_name: {}}
        for upkg in unitypackages:
            ret[self.rule_name][upkg.name] = upkg.toDict(with_hash)
        return ret
        """

    def __assetToMsg(self, asset: Optional[Asset]):
        return " GUID {0.guid} ({0.path})".format(asset) if asset else " < No Asset >"
