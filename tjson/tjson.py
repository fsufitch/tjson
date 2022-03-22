from __future__ import annotations
from warnings import warn
from typing import Dict, Generic, List, Optional, Sequence, Type, TypeVar, Union, cast

from tjson.errors import InvalidKeyWarning, TypeMismatchWarning


_JSONValue = Union[None, bool, str, int, float, List["_JSONValue"], Dict[str, "_JSONValue"]]
_T = TypeVar('_T', bound=_JSONValue)
_R = TypeVar('_R', bound=_JSONValue)


class TJ(Generic[_T]):
    def __init__(self, value: _T, path: Sequence[Union[int, str]] = [], warns: Sequence[Warning] = []):
        self._path = path
        self.value = value
        self.warnings = warns

    def __getitem__(self, key: Union[int, str]) -> TJ[_JSONValue]:
        next_path = (*self._path, key)
        if isinstance(key, int):
            if not isinstance(self.value, list):
                return TJ(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Cannot access int index {key} of non-array at path {self.path}"), 2))
            if key < 0 or key >= len(self.value):
                return TJ(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Out-of-bounds index {key} at path {self.path}"), 2))
            return TJ(self.value[key], next_path, self.warnings)

        if isinstance(key, str):
            if not isinstance(self.value, dict):
                return TJ(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Tried to access str key {repr(key)} of non-object at path `{self.path}`"), 2))
            if key not in self.value:
                return TJ(None, next_path, _amend_warns(self.warnings, InvalidKeyWarning(f"Missing key {repr(key)} at path {self.path}"), 2))
            return TJ(self.value[key], next_path, self.warnings)

        raise SyntaxError(f"Invalid node lookup: {key}")

    def __contains__(self, key: Union[int, str]) -> bool:
        if isinstance(key, int) and isinstance(self.value, list):
            return 0 <= key and key < len(self.value)
        if isinstance(key, str) and isinstance(self.value, dict):
            return key in self.value
        return False

    def __iter__(self):
        if isinstance(self.value, list):
            yield from (TJ(it, [*self._path, i], [*self.warnings]) for i, it in enumerate(self.value))
        elif isinstance(self.value, dict):
            yield from (TJ(it, [*self._path, k], [*self.warnings]) for k, it in self.value.items())
        else:
            warn(TypeMismatchWarning(f"Cannot iterate over {type(self.value)} at path {self.path}"), stacklevel=2)

    @property
    def path(self) -> str:
        parts = []
        for elem in self._path:
            if isinstance(elem, str) and elem.isalnum() and elem[0].isalpha():
                parts.append(f'.{elem}')
            else:
                parts.append('[{}]'.format(repr(elem)))
        return ''.join(parts)

    @property
    def bool(self) -> TJ[bool]:
        return self._cast(bool, 2)

    @property
    def bool_or_null(self) -> TJ[Optional[bool]]:
        return self._cast_or_null(bool, 2)

    @property
    def string(self) -> TJ[str]:
        return self._cast(str, 2)

    @property
    def string_or_null(self) -> TJ[Optional[str]]:
        return self._cast_or_null(str, 2)

    @property
    def number(self) -> TJ[Union[int, float]]:
        if not isinstance(self.value, (int, float)):
            return TJ(0, self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to int|float at path `{self.path}`"), 2))
        return cast(TJ[Union[int, float]], self)

    @property
    def number_or_null(self) -> TJ[Optional[Union[int, float]]]:
        if not isinstance(self.value, (int, float, type(None))):
            return TJ(None, self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to int|float|None at path `{self.path}`"), 2))
        return cast(TJ[Optional[Union[int, float]]], self)

    @property
    def array(self) -> TJ[List[_JSONValue]]:
        return self._cast(list, 2)

    @property
    def array_or_null(self) -> TJ[Optional[List[_JSONValue]]]:
        return self._cast_or_null(list, 2)  # type: ignore

    @property
    def object(self) -> TJ[Dict[str, _JSONValue]]:
        return self._cast(dict, 2)

    @property
    def object_or_null(self) -> TJ[Optional[Dict[str, _JSONValue]]]:
        return self._cast_or_null(dict, 2)

    def _cast(self, typ: Type[_R], stacklevel: int = 1) -> TJ[_R]:
        if not callable(typ):
            raise TypeError()
        if not isinstance(self.value, typ):
            return cast(TJ[_R], TJ(typ(), self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to {repr(typ)} at path `{self.path}`"), stacklevel + 1)))
        return cast(TJ[_R], self)

    def _cast_or_null(self, typ: Type[_R], stacklevel: int = 1) -> TJ[Optional[_R]]:
        if not isinstance(self.value, (typ, type(None))):
            return cast(TJ[Optional[_R]],
                        TJ(None, self._path, _amend_warns(self.warnings, TypeMismatchWarning(f"Cannot cast to {repr(typ)} or null at path `{self.path}`"), stacklevel + 1))
                        )
        return cast(TJ[Optional[_R]], self)


def _amend_warns(warns: Sequence[Warning], warning: Warning, stacklevel: int = 1) -> Sequence[Warning]:
    if not warns:
        warn(warning, stacklevel=stacklevel + 1)
    return (*warns, warning)
