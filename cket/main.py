from cket.exceptions import InvalidIdError
import argparse
import logging
import traceback
from typing import List
from srolib.util.easy_logger import setupLogger
from srolib.unity.unitypackage import Unitypackage


def main(inputs: List[str], prefix: str, suffix: str, output_dir: str, **kwargs):
    logger = logging.getLogger("main")
    for filepath in inputs:
        try:
            logger.info(f"Start: {filepath}")
            pass
            # upkg: Unitypackage = Unitypackage(filepath)
        except Exception as e:
            logger.error(f"Exception has occured. {type(e)} {str(e)}")
            logger.debug(traceback.format_exc())


def validateId(id_str: str):
    _id = int(id_str)
    if 0 <= _id < 999:
        return _id
    raise InvalidIdError(f"{id_str} is invalid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unitypackage validator for Cross market.")
    parser.add_argument("--debug",
                        help="output debug log.",
                        action="store_true")
    parser.add_argument("--output-dir",
                        help="output directory path. default is input directory.",
                        type=str,
                        default=None)
    parser.add_argument("--prefix",
                        help="prefix of output filename.",
                        type=str,
                        default="")
    parser.add_argument("--suffix",
                        help="suffix of output filename.",
                        type=str,
                        default="_validated")
    parser.add_argument("exhibitor-id",
                        help="exhibitor's id",
                        type=int)
    parser.add_argument("inputs",
                        help="input filepath.",
                        type=str,
                        nargs="+")

    args = parser.parse_args()
    setupLogger("cket",
                console_level=logging.DEBUG if args.debug else logging.INFO)

    main(**vars(args))
