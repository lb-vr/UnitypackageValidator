
class InvalidIdError(ValueError):
    pass


class InvalidDirectory(ValueError):
    pass


class InvalidRuleError(Exception):

    @classmethod
    def assertion(cls, cond, message=""):
        if not cond:
            raise cls(message)
