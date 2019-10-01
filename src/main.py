# (c) 2019 lb-vr - WhiteAtelier

import argparse
import logging

import logger_setup
import settings
from validator import validator

if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description='Unitypackage validator.')
    parser.add_argument('-b', '--batch', help='work on batch mode.', action='store_true')
    parser.add_argument('-f', '--filepath', help='output validating result formatted json. Default is no output.', type=str, default='')
    parser.add_argument('-s', '--settings', help='filepath of settings file.', type=str, default='settings.toml')
    parser.add_argument('-ru', '--rule-url', help='URL of rule file. If you specified, overwrite rule url settings.', type=str, default='')
    parser.add_argument('-rf', '--rule-filepath', help='filepath of rule file. If you specified, overwrite rule url settings.', type=str, default='')
    parser.add_argument('-q', '--quiet', help='mute stdout flag.', action='store_true')
    parser.add_argument('-rd', '--redirect', help='redirect output json string to stdout.', action='store_true')
    parser.add_argument('-l', '--log-level', help='select log level of stderr. default is "error"', choices=['debug', 'info', 'warn', 'error'], default='error')
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
        v = validator.Validator()
        v.do()

    else:
        # open ui but not implemented yet.
        raise RuntimeWarning('UI has not been implemented yet.')
