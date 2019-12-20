import os
import sys
import logging
import tempfile
import json
import urllib.request
import copy

from typing import List, Tuple

from PySide2 import QtGui, QtCore

from unitypackage import Unitypackage, Asset

from validators.includes_blacklist import IncludesBlacklist
from validators.filename_blacklist import FilenameBlacklist
from validators.modifiable_asset import ModifiableAsset
from validators.shader_includes import ShaderIncludes
from validators.reference_whitelist import ReferenceWhitelist
from validators.shader_namespace import ShaderNamespace
from validators.path_namespace import PathNamespace
from validators.reference_tree import ReferenceTree


class Validator(QtCore.QThread):

    finishedValidating = QtCore.Signal(tuple)
    progress = QtCore.Signal(int, str)

    def __init__(self, unitypackage_fpath: str, rule_url: str, id_string: str, destination: str, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.__unitypackage_fpath = unitypackage_fpath
        self.__rule_url = rule_url
        self.__id_string = id_string
        self.__destination = destination  # TODO:ここがNoneだったら、一時ディレクトリに保存する

    def run(self):
        ret = self.validator_main(self.__unitypackage_fpath, self.__rule_url, self.__id_string, self.__destination)
        self.finishedValidating.emit(ret)
        self.finished.emit()

    def validator_main(self,
                       unitypackage_fpath: str,
                       rule_url: str,
                       id_string: str,
                       destination: str)\
            -> Tuple[List[Tuple[str, List[str], List[str]]], Unitypackage, Unitypackage]:

        ret: List[Tuple[str, List[str], List[str]]] = []

        # to absolute path
        unitypackage_fpath = os.path.abspath(unitypackage_fpath)

        modified_unitypackage: Unitypackage = Unitypackage("")

        # Open File
        with tempfile.TemporaryDirectory() as tmpdir:
            print(tmpdir)
            # extract dir
            try:
                print("extracting tar.")
                self.reportProgress(5, "Extracting tar...")
                Unitypackage.extract(unitypackage_fpath, tmpdir)

                # set instance
                print("initializing unitypackage instance.")
                self.reportProgress(20, "initializing unitypackage instance...")
                unity_package = Unitypackage(os.path.basename(unitypackage_fpath))

                # load
                print("loading unitypackage.")
                self.reportProgress(25, "loading unitypackage...")
                unity_package.load(tmpdir)

                # unitypackageの準備はできた

                # load rule
                print("loading rulefile.")
                self.reportProgress(35, "loading rulefile...")
                rule: dict = {}

                with urllib.request.urlopen(rule_url) as f:
                    rule = json.loads(f.read().decode("utf-8"))

                self.reportProgress(40, "ReferenceTree...")
                print("ReferenceTree...")
                rt = ReferenceTree(unity_package, id_string)
                rt.run()
                ret.append(("参照マップによる削減", rt.getLog(), rt.getNotice()))

                # 1. 含んではいけないアセット
                # つまり、再配布禁止なもの、VRCSDK、アセットストアのもの、など。
                # ルール名は「includes_blacklist」
                print("IncludesBlacklist...")
                self.reportProgress(55, "IncludesBlacklist...")
                ib = IncludesBlacklist(unity_package, rule)
                ib.run()
                ret.append(("含んではいけないアセット", ib.getLog(), ib.getNotice()))

                # 2. 含んではいけないファイル群
                # ファイルに対するフィルタで、該当する者は削除する
                # ルール名は「filename_blacklist」
                # ファイル名は正規表現でマッチングを行う。
                # 例えば、.cs（スクリプトファイル）, *.dll, *.exe, *.blend, *.mb, *.maなど？
                print("FilenameBlacklist...")
                self.reportProgress(60, "FilenameBlacklist...")
                fb = FilenameBlacklist(unity_package, rule)
                fb.run()
                ret.append(("含んではいけないファイル", fb.getLog(), fb.getNotice()))

                # 3. 改変可能なアセットだが、全く未改変なファイル群
                # 改変した場合は含めなくてはいけないが、全く未改変なファイル群であれば削除する
                # とりあえず、削除する単位は、以下の例外を除いて、unitypackage単位とする
                # ルール名は「modifing_whitelist」
                # 例えば、シェーダーコード等である。

                # 3-1-1. それらが.shaderだった場合
                # 中で呼び出しているcgincファイルが、テストファイルの中に含まれているか確かめる
                # 含まれていなかったらエラー

                # 3-1-3. .cgincの一部が未改変だった場合
                # かつ、参照カウントを設けて、テストファイル内の、どの.shader, .cgincからもインクルードされていない場合は、それを削除する

                # 3-2 それらがTextureだった場合
                # 未改変なtextureは削除する
                print("ModifiableAsset...")
                self.reportProgress(65, "ModifiableAsset...")
                ma = ModifiableAsset(unity_package, rule)
                ma.run()
                ret.append(("改変可能な共通アセット", ma.getLog(), ma.getNotice()))

                # 4. 残った.shader、.cgincに対して、含まれるIncludesがAssets/からの絶対パスになっていないか
                # 処理が終わるとファイルパスがごっそり変わる
                # シェーダーファイルに対して絶対パスのincludeがあればエラーとする
                print("ShaderIncludes...")
                self.reportProgress(70, "ShaderIncludes...")
                ai = ShaderIncludes(unity_package, rule)
                ai.run()
                ret.append(("絶対パスインクルードを含んだシェーダー", ai.getLog(), ai.getNotice()))

                # 5. テクスチャファイル、シェーダーファイルに関して、参照されていないものを削除する
                # テクスチャもシェーダーも、unityに取り込んだ時点でコンパイルが走る。重たいので削除する
                # fa = FloatingAsset(unity_package)
                # fa.run()
                # ret.append(("参照されていないアセットの削除", fa.getLog(), []))

                # 6. 参照先不明なものをエラーとする
                # ここまでとことん削ったが、この後、自己参照・共通アセット参照のいずれでもないアセットを参照エラーとする。
                # ルール名は「reference_whitelist」
                print("ReferenceWhitelist...")
                self.reportProgress(75, "ReferenceWhitelist...")
                rw = ReferenceWhitelist(unity_package, rule)
                rw.run()
                ret.append(("共通アセット", rw.getLog(), rw.getNotice()))

                # 7. 再帰的に参照マップを作り、参照マップに乗らなかったものたちは全て削除

                # この時点でのUnitypackageを保存
                modified_unitypackage = copy.deepcopy(unity_package)

                # 8. 全てのshaderの名前空間を掘り下げる
                # 指定された文字列を頭につけて、名前空間を掘り下げる。
                print("ShaderNamespace...")
                self.reportProgress(80, "ShaderNamespace...")
                sn = ShaderNamespace(unity_package, id_string)
                sn.run()

                # 9. 全てのアセットのフォルダを、指定された文字列をルートフォルダとするように変更する
                print("PathNamespace...")
                self.reportProgress(85, "PathNamespace...")
                pn = PathNamespace(unity_package, id_string)
                pn.run()

                # 10. GUIDの再発行
                # ハッシュの衝突を防ぐために、変換マップを作成し、共有できるような仕組みを作りたいね
                # でもそこまでやんなくてもって感じだね

                ###########################################################################################

                # 1. 改変不可能なアセットが含まれていないか
                # つまり、このアセット群は含めてはいけないもの。
                # ルールとしては、「改変可能で含めても良いアセット」から漏れたものを削除する。
                # ルール名は「permitted_modifing」で、「改変可能、かつ改変時は含めて良いアセット」を指定する
                # prohibited_modifing = ProhibitedModifing(unity_package, rule)
                # prohibited_modifing.run()

                # 1. 未同梱・参照ファイルのチェック
                # reference_whitelist = ReferenceWhitelist(unity_package, rule)
                # reference_whitelist.run()

                # 2. 共通アセットが含まれているか
                # include_common_asset = IncludeCommonAsset(unity_package, rule)
                # include_common_asset.run()

                # 残ったアセットをリストアップ
                print("=======================================================", file=sys.stderr)
                for asset in unity_package.assets.values():
                    if not asset.deleted:
                        print(asset, file=sys.stderr)

                # unitypackageにパッキングし直し
                print("packing...")
                self.reportProgress(90, "packing...")
                unity_package.pack(tmpdir, destination)

                self.reportProgress(100, "Finished...")

            except FileNotFoundError as e:
                print(e, file=sys.stderr)

        return (ret, modified_unitypackage, unity_package)

    def reportProgress(self, value: int, line: str):
        self.progress.emit(value, line)
