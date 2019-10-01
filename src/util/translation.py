import os
import json
from typing import Dict


class __Translation:
    __dictionaly: Dict[str, str] = {}

    @classmethod
    def _append(cls, jdict):
        for k, v in jdict.items():
            if type(v) is str:
                cls.__dictionaly[k] = v
            elif type(v) is dict:
                cls._append(v)

    @classmethod
    def setupLocale(cls, lang: str) -> bool:
        path = os.path.join(os.path.join(os.path.join(os.getcwd(), 'locale'), lang), 'tr.json')
        if not os.path.exists(path):
            return False

        with open(path, mode='r', encoding='utf-8') as ftr:
            try:
                cls._append(json.load(ftr))
            except json.JSONDecodeError:
                return False
        return True

    @classmethod
    def getTranslation(cls, key: str) -> str:
        if key in cls.__dictionaly:
            return cls.__dictionaly[key]
        return key


def setupLocale(lang: str) -> bool:
    return __Translation.setupLocale(lang)


def tr(src: str) -> str:
    return __Translation.getTranslation(src)
