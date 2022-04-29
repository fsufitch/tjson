"""Centralized holding area for TJSON errors"""


class TJSONWarning(Warning):
    """Base TJSON warning"""


class InvalidKeyWarning(TJSONWarning):
    """Warning indicating a key was missing, inappropriate, or otherwise invalid"""


class TypeMismatchWarning(TJSONWarning):
    """Warning indicating that the type of an object did not match expectations"""
