# -*- coding: utf-8 -*-
"""IP address field class"""

import abc
import ipaddress
from typing import TYPE_CHECKING, TypeVar

from pcapkit.corekit.fields.field import Field, NoValue
from pcapkit.utilities.exceptions import FieldValueError

__all__ = [
    'IPv4Field',
    'IPv6Field',
]

if TYPE_CHECKING:
    from ipaddress import IPv4Address, IPv6Address
    from typing import Callable, Any

    from typing_extensions import Literal

    from pcapkit.corekit.fields.field import NoValueType


_T = TypeVar('_T', 'IPv4Address', 'IPv6Address')


class _IPField(Field[_T]):
    """Internal IP address value for protocol fields.

    Args:
        default: field default value, if any.
        callback: callback function to be called upon
            :meth:`self.__call__ <pcapkit.corekit.fields.field._Field.__call__>`.

    """

    @abc.abstractmethod
    @property
    def version(self) -> 'int':
        """IP version number."""

    def pre_process(self, value: '_T | bytes | int', packet: 'dict[str, Any]') -> 'bytes':
        """Process field value before packing.

        Args:
            value: field value.
            packet: packet data.

        Returns:
            Processed field value.

        """
        if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return value.packed
        if isinstance(value, int):
            return ipaddress.ip_address(value).packed
        if isinstance(value, bytes):
            return value
        raise FieldValueError(f'invalid IP address value: {value!r}')

    def post_process(self, value: 'bytes', packet: 'dict[str, Any]') -> '_T':
        """Process field value after parsing (unpacking).

        Args:
            value: field value.
            packet: packet data.

        Returns:
            Processed field value.

        """
        return ipaddress.ip_address(value)  # type: ignore[return-value]


class IPv4Field(_IPField[ipaddress.IPv4Address]):
    """IPv4 address value for protocol fields.

    Args:
        default: field default value, if any.
        callback: callback function to be called upon
            :meth:`self.__call__ <pcapkit.corekit.fields.field._Field.__call__>`.

    """

    @property
    def version(self) -> 'Literal[4]':
        """IP version number."""
        return 4

    def __init__(self, default: 'IPv4Address | NoValueType' = NoValue,
                 callback: 'Callable[[IPv4Field, dict[str, Any]], None]' = lambda *_: None) -> 'None':
        super().__init__(4, default, callback)  # type: ignore[arg-type]

        self._template = f'4s'


class IPv6Field(_IPField[ipaddress.IPv6Address]):
    """IPv6 address value for protocol fields.

    Args:
        default: field default value, if any.
        callback: callback function to be called upon
            :meth:`self.__call__ <pcapkit.corekit.fields.field._Field.__call__>`.

    """

    @property
    def version(self) -> 'Literal[6]':
        """IP version number."""
        return 6

    def __init__(self, default: 'IPv6Address | NoValueType' = NoValue,
                 callback: 'Callable[[IPv6Field, dict[str, Any]], None]' = lambda *_: None) -> 'None':
        super().__init__(16, default, callback)  # type: ignore[arg-type]

        self._template = f'16s'
