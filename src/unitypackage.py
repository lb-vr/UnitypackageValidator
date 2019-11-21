import logging
import os
import tarfile
import re
import enum
import shutil
from typing import List, Dict, Optional


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
    kShader = ("shader", "cginc")
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

    def delete(self):
        if not self.deleted:
            self.__deleted = True
            shutil.rmtree(self.root_dpath)

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
        except UnicodeDecodeError:
            pass
        return ret


#######################################################################################################################
# Unitypackage Class
# + __init__
# + load
# + extract
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
    def assets(self) -> Dict[str, Asset]:
        return self.__assets

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
