# -*- coding: utf-8 -*-

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable, Generator, Optional, Type, Union

__all__ = [
    # functions
    'final', 'localcontext',

    # exceptions
    'ModuleNotFoundError',

    # classes
    'Collection', 'cached_property',
    'Mapping', 'Tuple', 'List', 'Dict',
    'StrEnum',

    # modules
    'pathlib',
]

if sys.version_info < (3, 6):
    class ModuleNotFoundError(ImportError):  # pylint: disable=redefined-builtin
        """Module not found."""
else:
    from builtins import ModuleNotFoundError

if sys.version_info <= (3, 5):
    from collections.abc import Container, Iterable, Sized  # pylint: disable=unused-import

    def _check_methods(C: 'Type[Any]', *methods: 'str') -> 'bool | Any':
        mro = C.__mro__
        for method in methods:
            for B in mro:
                if method in B.__dict__:
                    if B.__dict__[method] is None:
                        return NotImplemented
                    break
            else:
                return NotImplemented
        return True

    class Collection(Sized, Iterable, Container):  # pylint: disable=abstract-method

        __slots__ = ()

        @classmethod
        def __subclasshook__(cls, C: 'Type[Any]') -> 'bool | Any':
            if cls is Collection:
                return _check_methods(C, "__len__", "__iter__", "__contains__")
            return NotImplemented
else:
    from collections.abc import Collection

if sys.version_info <= (3, 4):
    import pathlib2 as pathlib  # pylint: disable=import-error
else:
    import pathlib

# functools.cached_property added in 3.8
if sys.version_info < (3, 8):
    from threading import RLock
    from typing import Generic, TypeVar  # isort: split

    _T = TypeVar("_T")
    _S = TypeVar("_S")

    _NOT_FOUND = object()

    class cached_property(Generic[_T]):
        def __init__(self, func: 'Callable[[Any], _T]') -> 'None':
            self.func = func  # type: Callable[[Any], _T]
            self.attrname = None  # type: Optional[str]
            self.__doc__ = func.__doc__
            self.lock = RLock()

        def __set_name__(self, owner: 'Type[Any]', name: 'str') -> 'None':
            if self.attrname is None:
                self.attrname = name
            elif name != self.attrname:
                raise TypeError(
                    "Cannot assign the same cached_property to two different names "
                    f"({self.attrname!r} and {name!r})."
                )

        def __get__(self, instance: 'Optional[_S]',
                    owner: 'Optional[Type[Any]]' = None) -> 'Union[cached_property[_T], _T]':
            if instance is None:
                return self
            if self.attrname is None:
                raise TypeError(
                    "Cannot use cached_property instance without calling __set_name__ on it.")
            try:
                cache = instance.__dict__
            except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
                msg = (
                    f"No '__dict__' attribute on {type(instance).__name__!r} "
                    f"instance to cache {self.attrname!r} property."
                )
                raise TypeError(msg) from None
            val = cache.get(self.attrname, _NOT_FOUND)
            if val is _NOT_FOUND:
                with self.lock:
                    # check if another thread filled cache while we awaited lock
                    val = cache.get(self.attrname, _NOT_FOUND)
                    if val is _NOT_FOUND:
                        val = self.func(instance)
                        try:
                            cache[self.attrname] = val
                        except TypeError:
                            msg = (
                                f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                                f"does not support item assignment for caching {self.attrname!r} property."
                            )
                            raise TypeError(msg) from None
            return val
else:
    from functools import cached_property

if sys.version_info < (3, 9):
    from typing import Dict, List, Mapping, Tuple
else:
    from collections.abc import Mapping

    Tuple = tuple
    List = list
    Dict = dict

if sys.version_info < (3, 11):
    from aenum import StrEnum
else:
    from enum import StrEnum

if sys.version_info < (3, 8):
    from typing_extensions import final
else:
    from typing import final

if sys.version_info < (3, 11):
    from contextlib import contextmanager
    from decimal import localcontext as _localcontext

    if TYPE_CHECKING:
        from decimal import Context
        from types import TracebackType

        class _ContextManager:
            def __init__(self, new_context: Context) -> None: ...
            def __enter__(self) -> Context: ...
            def __exit__(self, t: type[BaseException] | None, v: BaseException | None, tb: TracebackType | None) -> None: ...

    @contextmanager
    def localcontext(ctx: 'Optional[Context]' = None, **kwargs: 'Any') -> '_ContextManager':
        """Return a context manager that will set the default context to a copy
        of ctx on entry to the with-statement and restore the previous default
        context when exiting the with-statement. If no context is specified, a
        copy of the current default context is used."""
        with _localcontext(ctx) as lc:
            for attr, value in kwargs.items():
                setattr(lc, attr, value)
            yield lc
else:
    from decimal import localcontext
