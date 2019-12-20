import logging
import tempfile
import os
import json
import argparse
import sys

from unitypackage import Unitypackage
from logger_setup import setupLogger
from ui.validator_main_ui import validator_main_ui

# Validator
# from validators.includes_blacklist import IncludesBlacklist
# from validators.reference_whitelist import ReferenceWhitelist
# from validators.include_common_asset import IncludeCommonAsset
# from validators.prohibited_modifing import ProhibitedModifing

# Rule Generator
from rule_generator.rule_generator import rule_generator_main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="unitypackageに対して、ルールの適用を行います。もしくはルールそのものを生成します。")
    parser.add_argument("-d", "--debug", help="ログレベルをDEBUGに設定します", action="store_true")
    parser.add_argument("-g", "--generator", help="RuleGeneratorを開きます", action="store_true")
    parser.add_argument("-b", "--batch", nargs=3, help="<input> <rule> <output>", default=None)
    parser.add_argument("-i", "--ignore", help="指定されたルールを無視します", nargs="+",
                        choices=["rt", "ib", "fb", "ma", "si", "sn", "pn", "gr"])
    parser.add_argument("-c", "--config", type=str, help="設定ファイルパス", default="cfg.ini")
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    args = parser.parse_args()

    setupLogger("UnitypackageTools", stderr_level=(logging.DEBUG if args.debug else logging.INFO))
    logging.getLogger().info("Current-directory: %s", os.getcwd())

    if args.generator:
        rule_generator_main()

    if args.batch is not None:
        pass

    else:
        validator_main_ui(args)
        # validator_main("test.unitypackage", "test.json")
        # validator_main(r"W:\testcase6.unitypackage",
        #                r"W:\vfrontier_rule.json", "65431154313246784234")
