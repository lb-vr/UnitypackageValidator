import os
import sys
import argparse
import logging
import traceback
import json
from srolib.util import easy_logger
from srolib.unity.unitypackage import Unitypackage
from cket import exceptions

from cket import rules


def main(eid: int, rule: list, infile: str, prefix: str, suffix: str, output_dir: str, report, **kwargs):
    logger: easy_logger.IndentedLogger = logging.getLogger("main")
    filepath = infile
    try:
        logger.info(f"Start: {filepath}")
        logger.indent()
        upkg: Unitypackage = Unitypackage(filepath)
        upkg.load()

        """
        インポート前段階で
        • 禁止されている拡張子のアセットはじく
        • 出展者IDのフォルダ以外のアセットをはじく
        • GUIDが重複しても上書きされないように
        """
        instances = rules.BaseRule.getRuleInstances(rule)

        for inst in instances:
            logger.debug(f"RUN: {inst.rule_name}")
            result = inst.run(upkg=upkg, eid=eid)
            logger.info(f"Finished: {inst.rule_name}")

            print(result.__repr__(), file=report, flush=True)

        upkg.pack(os.path.join(output_dir,
                               f"{prefix}{os.path.splitext(os.path.basename(infile))[0]}{suffix}.unitypackage"))
        del upkg

    except Exception as e:
        logger.error(f"Exception has occured. {type(e)} {str(e)}")
        logger.debug(traceback.format_exc())


def validateId(id_str: str):
    _id = int(id_str)
    if 0 <= _id < 999:
        return _id
    raise exceptions.InvalidIdError(f"{id_str} is invalid.")


def validateOutputDir(_dir: str):
    if not os.path.isdir(_dir):
        raise exceptions.InvalidDirectory(f"{_dir} is invalid directory path.")
    return _dir


def main_cket():
    parser = argparse.ArgumentParser(description="Unitypackage validator for Cross market.")
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("-v", "--verbose",
                     help="verbosity.",
                     action="count",
                     default=0)
    grp.add_argument("-q", "--quiet",
                     help="quiet mode.",
                     action="store_true")
    parser.add_argument("-d", "--debug",
                        help="output debug log.",
                        action="store_true")
    parser.add_argument("-o", "--output-dir",
                        help="output directory path. default is input directory.",
                        type=validateOutputDir,
                        default=None)
    parser.add_argument("-p", "--prefix",
                        help="prefix of output filename.",
                        type=str,
                        default="")
    parser.add_argument("-s", "--suffix",
                        help="suffix of output filename.",
                        type=str,
                        default="_validated")
    parser.add_argument("eid",
                        help="exhibitor's id",
                        type=validateId)
    parser.add_argument("rulefile",
                        help="rule json file.",
                        type=open)
    parser.add_argument("infile",
                        help="input filepath.",
                        type=str)
    parser.add_argument("-r", "--report",
                        help="prints report",
                        nargs="?",
                        type=argparse.FileType("w"),
                        const=sys.stdout,
                        default=os.devnull)

    args = parser.parse_args()

    # setup logger
    console_level = logging.INFO
    function_trace = False
    if args.quiet:
        console_level = logging.ERROR
    elif args.verbose:
        if args.verbose >= 2:
            function_trace = True
        if args.verbose >= 1:
            console_level = logging.DEBUG

    easy_logger.setupLogger("cket",
                            console_level=console_level,
                            function_trace_enabled=function_trace,
                            latest_logfile_path="latest.log",
                            latest_logfile_level=logging.DEBUG)

    logger: easy_logger.IndentedLogger = logging.getLogger("__main__")
    logger.debug("Arguments: ")
    logger.indent()

    # listup arguments
    if args.output_dir is None:
        args.output_dir = os.path.dirname(args.infile)
    for k, v in vars(args).items():
        logger.debug(f"{k} = {v}")

    # load rule
    jsondata = json.load(args.rulefile)

    # main
    main(rule=jsondata, **vars(args))


if __name__ == "__main__":
    main_cket()
