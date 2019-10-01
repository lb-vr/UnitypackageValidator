# (c) 2019 lb-vr - WhiteAtelier
import sys
import argparse
import logging
import getpass

import logger_setup
import settings
from validator import validator
from rule import rule

from util.translation import tr, setupLocale

if __name__ == "__main__":
    # translation
    if not setupLocale('jp_ja'):
        print('Failed to load language file.', file=sys.stderr)
        exit(-1)

    # parse arguments
    parser = argparse.ArgumentParser(description='Unitypackage validator.')
    parser.add_argument('-m', '--mode', help=tr('switch mode.'), choices=['validator', 'ruletool'], default='validator')
    parser.add_argument('-b', '--batch', help=tr('work on batch mode.'), action='store_true')
    parser.add_argument('-o', '--output', help=tr('output validating result formatted json.'), type=str, default='result.json')
    parser.add_argument('-s', '--settings', help=tr('filepath of settings file.'), type=str, default='settings.toml')
    parser.add_argument('-ru', '--rule-url', help=tr('URL of rule file. If you specified, overwrite rule url settings.'), type=str, default='')
    parser.add_argument('-rf', '--rule-filepath', help=tr('filepath of rule file. If you specified, overwrite rule url settings.'), type=str, default='')
    parser.add_argument('-q', '--quiet', help=tr('mute stdout flag.'), action='store_true')
    parser.add_argument('-rd', '--redirect', help=tr('redirect output json string to stdout.'), action='store_true')
    parser.add_argument('-l', '--log-level', help=tr('select log level of stderr. default is "error"'), choices=['debug', 'info', 'warn', 'error'], default='error')
    parser.add_argument('-pk', '--packages', help=tr('common asset unitypackages. only for ruletool.'), nargs='*', default=[])
    parser.add_argument('-a', '--author', help=tr('author name'), type=str, default=getpass.getuser())
    args = parser.parse_args()

    # setup logger
    lg = logger_setup.setupLogger('unitypackage-validator', {'debug': logging.DEBUG, 'info': logging.INFO, 'warn': logging.WARN, 'error': logging.ERROR}[args.log_level])

    # opening log
    lg.info('Unitypackage Validator version 0.0.1')
    lg.debug('arguments = %s', str(args))

    # load settings
    if not settings.GlobalSettings.loadFromFile(args.settings):
        exit(-1)

    # open ui or validating
    if args.batch:
        if args.mode == 'validator':
            v = validator.Validator()
            v.do()
        else:
            rule.batch_main(args)

    else:
        # open ui but not implemented yet.
        raise RuntimeWarning('UI has not been implemented yet.')
