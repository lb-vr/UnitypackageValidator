import logging
import tempfile
import os
import json
import argparse
import sys
from PySide2.QtWidgets import QApplication

# custom style
import qdarkstyle
# from unitypackage import Unitypackage
# from logger_setup import setupLogger
# from ui.validator_main_ui import validator_main_ui

# Validator
# from validators.includes_blacklist import IncludesBlacklist
# from validators.reference_whitelist import ReferenceWhitelist
# from validators.include_common_asset import IncludeCommonAsset
# from validators.prohibited_modifing import ProhibitedModifing

# Rule Generator
# from rule_generator.rule_generator import rule_generator_main

import generator
from rules import rule_loader


def gen_main(args):
    window = generator.GeneratorWindow(args)
    window.show()


def validate_main(args):
    pass


if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(__file__), ".."))
    # os.chdir(os.path.dirname(os.path.abspath(os.path.join(sys.argv[0], "../"))))

    parser = argparse.ArgumentParser(description="unitypackageに対して、ルールの適用を行います。もしくはルールそのものを生成します。")
    parser.add_argument("-d", "--debug", help="ログレベルをDEBUGに設定します", action="store_true")

    subp = parser.add_subparsers()

    subp_gen = subp.add_parser(name="generator")
    subp_gen.set_defaults(handler=gen_main)

    args = parser.parse_args()

    rule_loader.load()

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(pyside=True))

    # setupLogger("UnitypackageTools", stderr_level=(logging.DEBUG if args.debug else logging.INFO))
    # logging.getLogger().info("Current-directory: %s", os.getcwd())

    if hasattr(args, "handler"):
        args.handler(args)

    else:
        validate_main(args)

    sys.exit(app.exec_())
