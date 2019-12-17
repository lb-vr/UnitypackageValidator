import logging
import os
import tarfile
import re
import enum
import shutil
import hashlib
from typing import List, Dict, Optional, Union


#######################################################################################################################
# Errors Class
#######################################################################################################################
class InvalidUnitypackageError(Exception):
    def __init__(self, reason: str, unitypackage_name=None, unitypackage_fpath=None):
        if unitypackage_fpath:
            reason += " Unitypackage path is " + unitypackage_fpath
        elif unitypackage_name:
            reason += " Unitypackage name is " + unitypackage_name
        super().__init__(reason, unitypackage_name, unitypackage_fpath)


#######################################################################################################################
# Assert Class
# + getFromFilename
#######################################################################################################################
class AssetType(enum.Enum):
    kTexture = ("png", "jpg", "jpeg", "bmp")
    kHdrTexture = ("exr", "hdr", "tif", "tiff")
    kScene = ("unity",)
    kShader = ("shader", "cginc", "glslinc")
    kMaterial = ("mat",)
    kModel = ("fbx", "obj")
    kAnimation = ("anim", "controller")
    kPrefab = ("prefab",)
    kScript = ("cs",)
    kAsset = ("asset")

    kDir = ("",)
    kUnknown = ("*",)

    @classmethod
    def getFromFilename(cls, fname: str):
        """
        ファイル名からアセットの種類を解析し、AssetTypeの列挙メンバを返す。
        """
        _, ext = os.path.splitext(os.path.basename(fname))
        ext = ext.lower().replace(".", "")
        for item in AssetType.__members__.values():
            if ext in item.value:
                return item
        return cls.kUnknown


#######################################################################################################################
# Assert Class
# + __init__
# + guid
# + meta_fpath
# + data_fpath
# + path_fpath
# + path
# + references
# + filetype
# + load()
# - <classmethod> __getReferences()
#######################################################################################################################
class Asset:
    __logger = logging.getLogger("Asset")

    def __init__(self, guid: str, root_dpath: str):
        self.__guid: str = guid
        self.__root_dpath: str = root_dpath
        self.__path: Optional[str] = None
        self.__references: Optional[List[str]] = None
        self.__filetype: Optional[AssetType] = None
        self.__deleted: bool = False
        self.__hash = None
        self.__enabled: Optional[bool] = None

    @property
    def guid(self) -> str:
        return self.__guid

    @property
    def root_dpath(self) -> str:
        return self.__root_dpath

    @property
    def meta_fpath(self) -> str:
        return os.path.join(self.__root_dpath, "asset.meta")

    @property
    def data_fpath(self) -> str:
        return os.path.join(self.__root_dpath, "asset")

    @property
    def path_fpath(self) -> str:
        return os.path.join(self.__root_dpath, "pathname")

    @property
    def path(self) -> Optional[str]:
        return self.__path

    @property
    def hash(self) -> Optional[str]:
        return self.__hash

    @property
    def enabled(self) -> Optional[bool]:
        return self.__enabled

    @property
    def references(self) -> Optional[List[str]]:
        return self.__references

    @property
    def filetype(self) -> Optional[AssetType]:
        return self.__filetype

    @property
    def deleted(self) -> bool:
        return self.__deleted

    def load(self):
        # get pathname
        with open(self.path_fpath, mode="r") as fp:
            self.__path = fp.readline().strip()
        self.__filetype = AssetType.getFromFilename(self.path)

        # calc hash
        try:
            with open(self.data_fpath, mode="rb") as asset_data_f:
                self.__hash = hashlib.sha512(asset_data_f.read()).hexdigest()
        except FileNotFoundError:
            pass  # Directory

        # get references
        meta_ref = Asset.__getReferences(self.meta_fpath)
        data_ref = Asset.__getReferences(self.data_fpath)
        self.__references = meta_ref + data_ref  # Combine
        self.__references = list(set(self.references))

        # delete me
        try:
            while True:
                self.__references.remove(self.guid)
        except ValueError:
            pass

        Asset.__logger.debug("Asset: %s %s (%s) included %d reference(s).",
                             self.filetype.name, self.guid, self.path, len(self.references))

    def updatePath(self):
        # get pathname
        with open(self.path_fpath, mode="r") as fp:
            self.__path = fp.readline().strip()

    def delete(self):
        if not self.deleted:
            self.__deleted = True
            shutil.rmtree(self.root_dpath)

    def toDict(self, with_hash: bool = False, enabled: Optional[bool] = None) -> Dict[str, dict]:
        # Noneチェック
        assert self.path, '"path" must not be None. Did you call load() function?'
        assert self.filetype, '"filetype" must not be None. Did you call load() function?'
        assert not self.deleted, "This asset[{}] is deleted.".format(str(self))

        # 戻り値
        ret: Dict[str, dict] = {
            self.guid: {
                "guid": self.guid,
                "path": self.path,
                "type": self.filetype.name
            }
        }
        if enabled is not None:
            ret[self.guid]["enabled"] = enabled

        # ハッシュ生成
        if with_hash:
            ret[self.guid]["hash"] = self.hash

        return ret

    def __putFromJson(self, jdict: dict):
        self.__path = jdict["path"]
        try:
            self.__filetype = AssetType[jdict["type"]]
        except KeyError:
            self.__logger.error("Invalid filetype. Re-analyze from path: %s", self.__path)
            if self.__path is not None:
                self.__filetype = AssetType.getFromFilename(self.__path)
            else:
                self.__filetype = AssetType.kUnknown

        if "hash" in jdict:
            self.__hash = jdict["hash"]
        if "enabled" in jdict:
            self.__enabled = jdict["enabled"]

    @classmethod
    def createFromJsonDict(cls, jdict: dict):
        ret = Asset(jdict["guid"], "")
        ret.__putFromJson(jdict)
        return ret

    def __str__(self) -> str:
        return "{0.guid} ({0.path})".format(self)

    @classmethod
    def __getReferences(cls, fpath: str) -> List[str]:
        ret: List[str] = []
        guid_regex_rule = re.compile(r"guid: [0-9a-f]{32}")
        try:
            with open(fpath, mode="rt") as f:
                fstr = f.read()
                matched_list = guid_regex_rule.findall(fstr)
                for m in matched_list:
                    ret.append(m[6:])
        except FileNotFoundError:
            pass  # Directory
        except UnicodeDecodeError:
            pass
        return ret


#######################################################################################################################
# Unitypackage Class
# + __init__
# + name
# + assets
# + load()
# + extract()
#######################################################################################################################
class Unitypackage:

    def __init__(self, unitypackage_name: str):
        self.__unitypackage_name: str = unitypackage_name
        self.__assets: Dict[str, Asset] = {}
        self.__logger: logging.Logger = logging.getLogger("Unitypackage")
        self.__logger.debug("An unitypackage \"%s\" instance is initialized.", self.__unitypackage_name)

    def load(self, unitypackage_extracted_dirpath: str):
        # listup directories
        folders: List[str] = os.listdir(unitypackage_extracted_dirpath)

        # add asset
        for f in folders:
            self.__assets[f] = Asset(
                guid=f,
                root_dpath=os.path.join(unitypackage_extracted_dirpath, f))
            self.__assets[f].load()

    @property
    def name(self) -> str:
        return self.__unitypackage_name

    @property
    def assets(self) -> Dict[str, Asset]:
        return self.__assets

    def toDict(self, with_hash: bool = False) -> Dict[str, Dict[str, Dict[str, str]]]:
        ret: Dict[str, Dict[str, Dict[str, str]]] = {
            self.name: {}
        }
        for asset in self.assets.values():
            if not asset.deleted:
                ret[self.name].update(asset.toDict(with_hash))

        return ret

    def __putAssetFromJson(self, jdict: dict):
        for uuid, jasset in jdict.items():
            self.__assets[uuid] = Asset.createFromJsonDict(jasset)

    @classmethod
    def createFromJsonDict(cls, jdict: dict):
        assert len(list(jdict.keys())) == 1
        unitypackage_title = list(jdict.keys())[0]
        upkg: Unitypackage = Unitypackage(unitypackage_title)
        upkg.__putAssetFromJson(jdict[unitypackage_title])
        return upkg

    @classmethod
    def extract(cls, unitypackage_fpath: str, destination_dpath: str):
        logger: logging.Logger = logging.getLogger("Unitypackage")
        logger.debug("Extracting %s", unitypackage_fpath)

        # open tar
        with tarfile.open(unitypackage_fpath, "r:gz") as tar:
            tared_folders: List[str] = tar.getnames()
            logger.debug("- %d file(s) are included.", len(tared_folders))

            # check filename
            regex_rule = re.compile(r"^[0-9a-f]{32}(/asset|/asset.meta|/pathname|/preview.png)?$")
            for tf in tared_folders:
                logger.debug("-- %s", tf)
                if not regex_rule.match(tf):
                    raise InvalidUnitypackageError(reason="Invalid folder name.", unitypackage_fpath=unitypackage_fpath)

            # extract tar
            logger.debug("- Extracting.")
            tar.extractall(path=destination_dpath)
            logger.debug("- Extracted.")
