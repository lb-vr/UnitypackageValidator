import os
import logging
import toml

from util.json_util import fetchValue as _fetch


class GlobalSettings:
    __logger = None

    @classmethod
    def getLogger(cls) -> logging.Logger:
        if not cls.__logger:
            cls.__logger = logging.getLogger('GlobalSettings')
        return cls.__logger

    @classmethod
    def loadFromFile(cls, filepath: str) -> bool:
        logger = cls.getLogger()
        if not filepath:
            logger.fatal('setting filepath is empty.')
            return False

        if not os.path.exists(filepath):
            logger.fatal('setting file does not exist.')
            return False

        with open(filepath, mode='r', encoding='utf-8') as fstg:
            try:
                jstg = toml.load(fstg)

                # rule settings
                RuleSettings.rule_filepath = _fetch(jstg, 'rule.filepath')
                RuleSettings.rule_url = _fetch(jstg, 'rule.url')

            except toml.TomlDecodeError:
                logger.fatal('setting file is invalid as toml.')
                return False
        return True


class RuleSettings:

    rule_filepath: str = ''
    rule_url: str = ''

    @classmethod
    def loadFromFile(cls, filepath: str) -> bool:
        pass

    @classmethod
    def loadFromURL(cls, filepath: str) -> bool:
        pass
