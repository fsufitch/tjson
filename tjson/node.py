from __future__ import annotations
from warnings import warn
from typing import Any, Dict, Generic, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, Union, cast
import warnings


_JSONValue = Union[None, bool, str, int, float, List["_JSONValue"], Dict[str, "_JSONValue"]]
_T = TypeVar('_T', bound=_JSONValue)
_R = TypeVar('_R', bound=_JSONValue)

class TJSONWarning(Warning):
    pass

class InvalidKeyWarning(TJSONWarning):
    pass

class TypeMismatchWarning(TJSONWarning):
    pass


class Node(Generic[_T]):
    def __init__(self, value: _T, path: Sequence[Union[int, str]], warns: Sequence[Warning]):
        self._path = path
        self.value = value
        self.warnings = warns

    def __getitem__(self, key: Union[int, str]) -> Node[_JSONValue]:
        next_path = (*self._path, key)
        if isinstance(key, int):
            if not isinstance(self.value, list):
                return Node(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Cannot access int index {key} of non-array at path {self.path}"), 2))
            if key < 0 or key >= len(self.value):
                return Node(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Out-of-bounds index {key} at path {self.path}"), 2))
            return Node(self.value[key], next_path, self.warnings)

        if isinstance(key, str):
            if not isinstance(self.value, dict):
                return Node(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Tried to access str key {repr(key)} of non-object at path `{self.path}`"), 2))
            if key not in self.value:
                return Node(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Missing key {repr(key)} at path {self.path}"), 2))
            return Node(self.value[key], next_path, self.warnings)
    
        raise SyntaxError(f"Invalid node lookup: {key}")
    
    def __contains__(self, key: Union[int, str]) -> bool:
        if isinstance(key, int) and isinstance(self.value, list):
            return 0 <= key and key < len(self.value)
        if isinstance(key, str) and isinstance(self.value, dict):
            return key in self.value
        return False

    def __iter__(self):
        if isinstance(self.value, list):
            yield from enumerate(cast(_JSONValue, it) for it in self.value)
            return
        if isinstance(self.value, dict):
            yield from cast(Dict[str, _JSONValue], self.value).items()
            return
        warn(TypeMismatchWarning(f"Cannot iterate over {type(self.value)} at path {self.path}"), stacklevel=2)
        yield from []

    @property
    def path(self) -> str:
        parts = []
        fmt_dot = lambda k: f".{k}"
        fmt_bracket = lambda k: '[{}]'.format(repr(k))
        for elem in self._path:
            if isinstance(elem, str) and elem.isalnum() and elem[0].isalpha():
                parts.append(fmt_dot(elem))
            else:
                parts.append(fmt_bracket(elem))
        return ''.join(parts)

    @property
    def bool(self) -> Node[bool]:
        return self._cast(bool, 2)

    @property
    def bool_or_null(self) -> Node[Optional[bool]]:
        return self._cast_or_null(bool, 2)

    @property
    def string(self) -> Node[str]:
        return self._cast(str, 2)
        
    @property
    def string_or_null(self) -> Node[Optional[str]]:
        return self._cast_or_null(str, 2)

    @property
    def number(self) -> Node[Union[int, float]]:
        if not isinstance(self.value, (int, float)):
            return Node(0, self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to int|float at path `{self.path}`"), 2))
        return cast(Node[Union[int, float]], self)

    @property
    def number_or_null(self) -> Node[Optional[Union[int, float]]]:
        if not isinstance(self.value, (int, float, type(None))):
            return Node(None, self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to int|float|None at path `{self.path}`"), 2))
        return cast(Node[Optional[Union[int, float]]], self)
        
    @property
    def array(self) -> Node[List[_JSONValue]]:
        return self._cast(list, 2)
        
    @property
    def array_or_null(self) -> Node[Optional[List[_JSONValue]]]:
        return self._cast_or_null(list, 2)  # type: ignore

    @property
    def object(self) -> Node[Dict[str, _JSONValue]]:
        return self._cast(dict, 2)
        
    @property
    def object_or_null(self) -> Node[Optional[Dict[str, _JSONValue]]]:
        return self._cast(dict, 2)

    def _cast(self, typ: Type[_R], stacklevel: int = 1) -> Node[_R]:
        if typ is type(None) or not callable(typ):
            raise TypeError()
        if not isinstance(self.value, typ):
            return cast(Node[_R], Node(typ(), self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to {repr(typ)} at path `{self.path}`"), stacklevel + 1)))
        return cast(Node[_R], self)

    def _cast_or_null(self, typ: Type[_R], stacklevel: int = 1) -> Node[Optional[_R]]:
        if not isinstance(self.value, (typ, type(None))):
            return cast(Node[Optional[_R]], Node(None, self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to {repr(typ)} or null at path `{self.path}`"), stacklevel + 1)))
        return cast(Node[Optional[_R]], self)

def _amend_warns(warns: Sequence[Warning], warning: Warning, stacklevel: int = 1) -> Sequence[Warning]:
    if not warns:
        warn(warning, stacklevel= stacklevel + 1)
    return (*warns, warning)
