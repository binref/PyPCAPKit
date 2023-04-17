# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,consider-using-f-string
"""Dual Stack MIPv6 (DSMIPv6) IPv4 Home Address Option Status Codes
======================================================================

This module contains the constant enumeration for **Dual Stack MIPv6 (DSMIPv6) IPv4 Home Address Option Status Codes**,
which is automatically generated from :class:`pcapkit.vendor.mh.dsmipv6_status_code.DSMIPv6StatusCode`.

"""

from aenum import IntEnum, extend_enum

__all__ = ['DSMIPv6StatusCode']


class DSMIPv6StatusCode(IntEnum):
    """[DSMIPv6StatusCode] Dual Stack MIPv6 (DSMIPv6) IPv4 Home Address Option Status Codes"""

    #: Success [:rfc:`5555`]
    Success = 0

    #: Failure, reason unspecified [:rfc:`5555`]
    Failure_reason_unspecified = 128

    #: Administratively prohibited [:rfc:`5555`]
    Administratively_prohibited = 129

    #: Incorrect IPv4 home address [:rfc:`5555`]
    Incorrect_IPv4_home_address = 130

    #: Invalid IPv4 address [:rfc:`5555`]
    Invalid_IPv4_address = 131

    #: Dynamic IPv4 home address assignment not available [:rfc:`5555`]
    Dynamic_IPv4_home_address_assignment_not_available = 132

    #: Prefix allocation unauthorized [:rfc:`5555`]
    Prefix_allocation_unauthorized = 133

    @staticmethod
    def get(key: 'int | str', default: 'int' = -1) -> 'DSMIPv6StatusCode':
        """Backport support for original codes.

        Args:
            key: Key to get enum item.
            default: Default value if not found.

        """
        if isinstance(key, int):
            return DSMIPv6StatusCode(key)
        if key not in DSMIPv6StatusCode._member_map_:  # pylint: disable=no-member
            extend_enum(DSMIPv6StatusCode, key, default)
        return DSMIPv6StatusCode[key]  # type: ignore[misc]

    @classmethod
    def _missing_(cls, value: 'int') -> 'DSMIPv6StatusCode':
        """Lookup function used when value is not found.

        Args:
            value: Value to get enum item.

        """
        if not (isinstance(value, int) and 0 <= value <= 255):
            raise ValueError('%r is not a valid %s' % (value, cls.__name__))
        if 1 <= value <= 127:
            #: Unassigned
            extend_enum(cls, 'Unassigned_%d' % value, value)
            return cls(value)
        if 134 <= value <= 255:
            #: Unassigned
            extend_enum(cls, 'Unassigned_%d' % value, value)
            return cls(value)
        return super()._missing_(value)
