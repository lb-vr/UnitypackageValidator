import logging
import json
import re
import os

from unitypackage import AssetType, Asset, Unitypackage

from typing import List


class ReferenceTree:
    __logger = logging.getLogger("ReferenceTree")

    def __init__(self, unitypackage, namespace: str):
        self.__unitypackage: Unitypackage = unitypackage
        self.__namespace: str = namespace
        self.__logger = ReferenceTree.__logger

    def run(self) -> bool:
        self.__logger.info("Modifing ReferenceTree.")

        def _traversal(asset: Asset, unitypackage: Unitypackage, traversaled_list: List[str]):
            ret = {}
            for ref in asset.references:
                for asts in unitypackage.assets.values():
                    if asts.deleted:
                        continue
                    if ref == asts.guid and ref not in traversaled_list:
                        ret[asts] = _traversal(asts, unitypackage, traversaled_list + [asset.guid])
            if asset.filetype == AssetType.kShader:
                # インクルード解析
                includes = self.extractShaderIncludes(asset)
                for inc in includes:
                    ret[inc] = _traversal(inc, unitypackage, traversaled_list + [asset.guid])

            return ret

        # まずprefab
        tree: dict = {}
        for asset in self.__unitypackage.assets.values():
            if self.__namespace + ".prefab" in asset.path:
                # if "kaden_sporadic-e.prefab" in asset.path:
                if tree:
                    self.__logger.warning("[FATAL] There are some {}.prefab".format(self.__namespace))
                    return False
                tree[asset] = _traversal(asset, self.__unitypackage, [asset.guid])

        def _show(dct: dict):
            ret: dict = {}
            for k, v in dct.items():
                ret[k.path] = _show(v)
            return ret

        self.__logger.debug("Show Reference Tree ====")
        json_strs = json.dumps(_show(tree), indent=4).splitlines()
        for line in json_strs:
            self.__logger.debug("RefTree > %s", line)
        self.__logger.debug("====")

        # リファレンスをもとに削除
        def _search(dct: dict, target: Asset) -> bool:
            for k, v in dct.items():
                if k.guid == target.guid:
                    return True
                if _search(v, target):
                    return True
            return False

        for asset in self.__unitypackage.assets.values():
            if asset.deleted:
                continue
            if not _search(tree, asset):
                self.__logger.warning("[ FIX ] Deleted no referenced file. %s", asset)
                asset.delete()

        return True

    def extractShaderIncludes(self, target_asset: Asset, encoding: str = "utf-8") -> List[Asset]:
        ret: List[Asset] = []
        try:
            with open(target_asset.data_fpath, mode="r", encoding=encoding) as sf:
                self.__logger.debug("- Checking shader file. %s", target_asset)

                shader_body = sf.read()
                while True:
                    start_pos = shader_body.find("/*")
                    end_pos = shader_body.find("*/", start_pos)
                    if start_pos != -1 and end_pos != -1:
                        shader_body = shader_body[:start_pos] + shader_body[end_pos:]
                    else:
                        break

                shader_body = re.sub(r'/\*[^(\*/)]*\*/', '', shader_body)

                includes: List[str] = re.findall(r'^\s*#include "(?P<include_path>[^"]+)"', shader_body, re.MULTILINE)
                dirnm: str = os.path.dirname(target_asset.path)
                for inc in includes:
                    self.__logger.debug("-- includes: %s", inc)

                    # インクルード先が含まれているか
                    p = os.path.normpath(os.path.join(dirnm, inc.lower())).replace("\\", "/")
                    for aitm in self.__unitypackage.assets.values():
                        tmp = aitm.path.split("/")
                        tmp[-1] = tmp[-1].lower()

                        if "/".join(tmp) == p:
                            self.__logger.debug("- Found required cginc file. %s includes %s.", target_asset.path, p)
                            ret.append(aitm)
                            break  # found

        except UnicodeDecodeError:
            if encoding == "utf-8":
                self.__logger.warning("This shader is not utf-8 OMG. %s", target_asset)
                return self.extractShaderIncludes(target_asset, "sjis")
            else:
                self.__logger.warning("This shader is not shift-jis too, WTF!? %s", target_asset)
                return []

        return ret
