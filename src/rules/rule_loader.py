import os
import importlib


_generators = []
_validators = []


def load() -> list:
    modules = []
    root = os.path.dirname(__file__)
    for d in [f for f in os.listdir(root) if os.path.exists(os.path.join(root, f, "__init__.py"))]:
        mod = importlib.import_module(f"rules.{d}")
        if hasattr(mod, "Generator"):
            _generators.append(getattr(mod, "Generator"))
        if hasattr(mod, "run"):
            _validators.append(getattr(mod, "run"))
        modules.append(mod)

    return modules


def getGenerators() -> list:
    return _generators


def getValidators() -> list:
    return _validators
