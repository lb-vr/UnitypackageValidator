from typing import Any, Type, Union, Dict, List


def fetchValue(jstg, key: str, default: Any = '', except_type: Type = str) -> Any:
    keys = key.split('.')
    target = jstg
    for k in keys:
        if k not in target:
            return default
        target = target[k]
    return target if type(target) is except_type else default
