import sys
import logging
import tempfile
import datetime


def __handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.getLogger().exception("Exception has occured.", exc_info=(exc_type, exc_value, exc_traceback))


def setupLogger(file_prefix: str, stderr_level=logging.INFO, logfile_level=logging.DEBUG) -> logging.Logger:
    assert file_prefix, 'Invalid Argument: file_prefix'

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)-7s] %(asctime)s::%(name)-24s | %(message)s')

    # stderr
    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(stderr_level)
    stderr_handler.setFormatter(formatter)
    logger.addHandler(stderr_handler)

    # file
    strnow = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fname = tempfile.mktemp('.log', file_prefix + strnow + '-')
    print(':: Logging to ' + fname, file=sys.stderr)
    file_handler = logging.FileHandler(filename=fname, mode='w', encoding='utf-8')
    file_handler.setLevel(logfile_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # exception hook
    # sys.excepthook = __handle_exception

    return logger
