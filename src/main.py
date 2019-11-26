import logging
import tempfile
import os
import json
import argparse

from unitypackage import Unitypackage
from logger_setup import setupLogger

# Validator
from validators.core import validator_main
#from validators.includes_blacklist import IncludesBlacklist
#from validators.reference_whitelist import ReferenceWhitelist
#from validators.include_common_asset import IncludeCommonAsset
#from validators.prohibited_modifing import ProhibitedModifing

# Rule Generator
from rule_generator.rule_generator import rule_generator_main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="unitypackageに対して、ルールの適用を行います。もしくはルールそのものを生成します。")
    parser.add_argument("-g", "--generator", help="RuleGeneratorを開きます", action="store_true")
    parser.add_argument("-d", "--debug", help="ログレベルをDEBUGに設定します", action="store_true")
    args = parser.parse_args()

    setupLogger("UnitypackageTools", stderr_level=(logging.DEBUG if args.debug else logging.INFO))
    logging.getLogger().info("Current-directory: %s", os.getcwd())

    if args.generator:
        rule_generator_main()

    else:
        # validator_main("test.unitypackage", "test.json")
        validator_main(r"W:\testcase1.unitypackage", "test.json", "29310049234")
