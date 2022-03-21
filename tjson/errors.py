from typing import Literal


ErrorMode = Literal['raise', 'warn', 'silent']

def _handle_exception(mode: ErrorMode, exc: Exception):
    ...



class TJSONWarning(Warning):
    pass

class InvalidKeyWarning(TJSONWarning):
    pass

class TypeMismatchWarning(TJSONWarning):
    pass

