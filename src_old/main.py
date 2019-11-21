# (c) 2019 lb-vr - WhiteAtelier
import sys
import argparse
import logging
import getpass

from . import logger_setup
from . import settings
from .analyzer import analyzer
from .rule import rule


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description='Unitypackage validator.')
    parser.add_argument('-m', '--mode', help='switch mode.', choices=['validator', 'makerule'], default='validator')
    parser.add_argument('-b', '--batch', help='work on batch mode.', action='store_true')
    parser.add_argument('-q', '--quiet', help='mute stdout flag.', action='store_true')
    parser.add_argument('-i', '--import-packages', help='common asset unitypackage(s).', nargs='*', default=[])
    parser.add_argument('-o', '--output', help='output validating result formatted json.', type=str, default='result.json')
    parser.add_argument('-s', '--settings', help='filepath of settings file.', type=str, default='settings.toml')
    parser.add_argument('-a', '--author', help='author name', type=str, default=getpass.getuser())
    parser.add_argument('-r', '--rule', help='URL of rule file. If you specified, overwrite rule url settings.', type=str, default='')
    # parser.add_argument('-rd', '--redirect', help='redirect output json string to stdout.', action='store_true')
    parser.add_argument('-l', '--log', help='select log level of stderr. default is "error"', choices=['debug', 'info', 'warn', 'error'], default='error')
    args = parser.parse_args()

    # setup logger
    lg = logger_setup.setupLogger('unitypackage-validator', {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR}[args.log])

    # opening log
    lg.info('Unitypackage Validator version 0.0.1')
    lg.debug('arguments = %s', args)

    # load settings
    if not settings.GlobalSettings.loadFromFile(args.settings):
        exit(-1)

    # open ui or validating
    if args.batch:
        if args.mode == 'validator':
            analyzer.batch_main(args)
        else:
            rule.batch_main(args)
    else:
        # open ui but not implemented yet.
        raise RuntimeWarning('UI has not been implemented yet.')
