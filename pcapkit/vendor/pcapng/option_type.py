# -*- coding: utf-8 -*-
"""Option Types
==================

.. module:: pcapkit.vendor.pcapng.option_type

This module contains the vendor crawler for **Option Types**,
which is automatically generating :class:`pcapkit.const.pcapng.option_type.OptionType`.

"""

import collections
import sys
from typing import TYPE_CHECKING

import bs4

from pcapkit.vendor.default import Vendor

__all__ = ['OptionType']

if TYPE_CHECKING:
    from collections import Counter
    from typing import Callable

    from bs4.element import Tag

LINE = lambda NAME, DOCS, FLAG, ENUM, MISS, MODL: f'''\
# -*- coding: utf-8 -*-
# mypy: disable-error-code=assignment
# pylint: disable=line-too-long,consider-using-f-string
"""{(name := DOCS.split(' [', maxsplit=1)[0])}
{'=' * (len(name) + 6)}

.. module:: {MODL.replace('vendor', 'const')}

This module contains the constant enumeration for **{name}**,
which is automatically generated from :class:`{MODL}.{NAME}`.

"""
from typing import TYPE_CHECKING

from aenum import StrEnum, extend_enum

__all__ = ['{NAME}']

if TYPE_CHECKING:
    from typing import Optional, Type


class {NAME}(StrEnum):
    """[{NAME}] {DOCS}"""

    if TYPE_CHECKING:
        #: Short name of the option type.
        opt_name: 'str'
        #: Numeric value of the option type.
        opt_value: 'int'

    def __new__(cls, value: 'int', name: 'Optional[str]' = None) -> 'Type[{NAME}]':
        if name is None:
            name = 'opt_unknown'
        temp = '%d_%s' % (value, name)

        obj = str.__new__(cls, temp)
        obj._value_ = temp

        obj.opt_name = name
        obj.opt_value = value

        return obj

    def __repr__(self) -> 'str':
        return "<%s.%s: %d>" % (self.__class__.__name__, self.opt_name, self.opt_value)

    {ENUM}

    @staticmethod
    def get(key: 'int | str', default: 'int' = -1, *, namespace: 'str' = 'opt') -> '{NAME}':
        """Backport support for original codes.

        Args:
            key: Key to get enum item.
            default: Default value if not found.
            namespace: Namespace of the enum item.

        :meta private:
        """
        if isinstance(key, int):
            for enum_key, enum_val in {NAME}.__members__.items():
                if (enum_key.startswith(namespace) or enum_key.startswith('opt')) and enum_val.opt_value == key:
                    return enum_val
            return extend_enum({NAME}, 'opt_unknown_%d' % key, key, 'opt_unknown')
        if key not in {NAME}._member_map_:  # pylint: disable=no-member
            return extend_enum({NAME}, key, default)
        return {NAME}[key]  # type: ignore[misc]

    @classmethod
    def _missing_(cls, value: 'int') -> '{NAME}':
        """Lookup function used when value is not found.

        Args:
            value: Value to get enum item.

        """
        if not ({FLAG}):
            raise ValueError('%r is not a valid %s' % (value, cls.__name__))
        {MISS}
        {'' if ''.join(MISS.splitlines()[-1:]).startswith('return') else 'return super()._missing_(value)'}
'''.strip()  # type: Callable[[str, str, str, str, str, str], str]


class OptionType(Vendor):
    """Option Types"""

    #: Value limit checker.
    FLAG = 'isinstance(value, int) and 0 <= value <= 0xFFFF'
    #: Link to registry.
    LINK = 'https://www.ietf.org/staging/draft-tuexen-opsawg-pcapng-02.html'

    def count(self, data: 'list[str]') -> 'Counter[str]':
        """Count field records."""
        return collections.Counter()

    def request(self, text: 'str') -> 'dict[str, list[Tag]]':  # type: ignore[override] # pylint: disable=signature-differs
        """Fetch registry table.

        Args:
            text: Context from :attr:`~LinkType.LINK`.

        Returns:
            Rows (``tr``) from registry table (``table``).

        """
        soup = bs4.BeautifulSoup(text, 'html5lib')
        table_1 = soup.select('table#table-1')[0]
        table_3 = soup.select('table#table-3')[0]
        table_4 = soup.select('table#table-4')[0]
        table_7 = soup.select('table#table-7')[0]
        table_8 = soup.select('table#table-8')[0]
        table_10 = soup.select('table#table-10')[0]
        return {
            'table-1': table_1.select('tr')[1:],
            'table-3': table_3.select('tr')[1:],
            'table-4': table_4.select('tr')[1:],
            'table-7': table_7.select('tr')[1:],
            'table-8': table_8.select('tr')[1:],
            'table-10': table_10.select('tr')[1:],
        }

    def process(self, data: 'dict[str, list[Tag]]') -> 'tuple[list[str], list[str]]':  # type: ignore[override]
        """Process registry data.

        Args:
            data: Registry data.

        Returns:
            Enumeration fields and missing fields.

        """
        enum = []  # type: list[str]
        miss = [
            "return extend_enum(cls, 'opt_unknown_%d' % value, value, 'opt_unknown')",
        ]  # type: list[str]

        for content in data['table-1']:
            name = content.select('td')[0].text.strip()
            temp = content.select('td')[1].text.strip()

            try:
                code = int(temp)

                pref = f"{name}: 'OptionType' = {code}, {name!r}"
                sufs = self.wrap_comment(name)

                enum.append(f'#: {sufs}\n    {pref}')
            except ValueError:
                opts = tuple(map(lambda x: int(x), temp.split('/')))

                for code in opts:
                    pref = f"{name}_{code}: 'OptionType' = {code}, {name!r}"
                    sufs = self.wrap_comment(name)

                    enum.append(f'#: {sufs}\n    {pref}')

        for content in data['table-3']:
            name = content.select('td')[0].text.strip()
            code = content.select('td')[1].text.strip()

            pref = f"{name}: 'OptionType' = {int(code)}, {name!r}"
            sufs = self.wrap_comment(name)

            enum.append(f'#: {sufs}\n    {pref}')

        for content in data['table-4']:
            name = content.select('td')[0].text.strip()
            code = content.select('td')[1].text.strip()

            pref = f"{name}: 'OptionType' = {int(code)}, {name!r}"
            sufs = self.wrap_comment(name)

            enum.append(f'#: {sufs}\n    {pref}')

        for content in data['table-7']:
            name = content.select('td')[0].text.strip()
            code = content.select('td')[1].text.strip()

            pref = f"{name}: 'OptionType' = {int(code)}, {name!r}"
            sufs = self.wrap_comment(name)

            enum.append(f'#: {sufs}\n    {pref}')

        for content in data['table-8']:
            name = content.select('td')[0].text.strip()
            code = content.select('td')[1].text.strip()

            pref = f"{name}: 'OptionType' = {int(code)}, {name!r}"
            sufs = self.wrap_comment(name)

            enum.append(f'#: {sufs}\n    {pref}')

        for content in data['table-10']:
            name = content.select('td')[0].text.strip()
            code = content.select('td')[1].text.strip()

            pref = f"{name}: 'OptionType' = {int(code)}, {name!r}"
            sufs = self.wrap_comment(name)

            enum.append(f'#: {sufs}\n    {pref}')

        return enum, miss

    def context(self, soup: 'dict[str, list[Tag]]') -> 'str':  # type: ignore[override]
        """Generate constant context.

        Args:
            data: CSV data.

        Returns:
            Constant context.

        """
        enum, miss = self.process(soup)

        ENUM = '\n\n    '.join(map(lambda s: s.rstrip(), enum)).strip()
        MISS = '\n        '.join(map(lambda s: s.rstrip(), miss)).strip()

        return LINE(self.NAME, self.DOCS, self.FLAG, ENUM, MISS, self.__module__)


if __name__ == '__main__':
    sys.exit(OptionType())  # type: ignore[arg-type]
