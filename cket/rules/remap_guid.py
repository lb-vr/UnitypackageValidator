from typing import List, Dict
import hashlib
from srolib.unity.unitypackage import Unitypackage
from cket import exceptions
from .base import BaseRule, Result
from srolib.util import easy_logger


@easy_logger.easy_logging
class RemapGuidRule(BaseRule):

    def __init__(self):
        super().__init__()

    def run(self, upkg: Unitypackage, **kwargs) -> Result:
        result: Result = Result(self)
        guid_map: Dict[str, str] = {}
        while True:
            guid_map = {a.guid: hashlib.md5(a.guid.encode()).hexdigest() for a in upkg.assets.values()}
            if len(set(guid_map.keys()) | set(guid_map.values())) == len(upkg.assets) * 2:
                break
            self.logger.debug("Wow, Hash collision!!!")

        for asset in upkg.assets.values():
            before = asset.guid
            self.logger.debug(f"Remap {asset.filename} guid. {asset.guid} -> {guid_map[asset.guid]}")
            asset.remapGuid(guid_map)
            result.reportSuccess(asset, f"Remapped. (before: {before})")

        return result

    @classmethod
    def jsonKey(cls) -> str:
        return "remap_guid"
