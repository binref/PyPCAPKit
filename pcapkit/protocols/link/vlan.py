# -*- coding: utf-8 -*-
"""802.1Q customer VLAN tag type

:mod:`pcapkit.protocols.link.vlan` contains
:class:`~pcapkit.protocols.link.vlan.VLAN`
only, which implements extractor for 802.1Q
Customer VLAN Tag Type [*]_, whose structure is
described as below:

======= ========= ====================== =============================
Octets      Bits        Name                    Description
======= ========= ====================== =============================
  1           0   ``vlan.tci``              Tag Control Information
  1           0   ``vlan.tci.pcp``          Priority Code Point
  1           3   ``vlan.tci.dei``          Drop Eligible Indicator
  1           4   ``vlan.tci.vid``          VLAN Identifier
  3          24   ``vlan.type``             Protocol (Internet Layer)
======= ========= ====================== =============================

.. [*] https://en.wikipedia.org/wiki/IEEE_802.1Q

"""
from typing import TYPE_CHECKING

from pcapkit.const.vlan.priority_level import PriorityLevel as RegType_PriorityLevel
from pcapkit.protocols.data.link.vlan import TCI as DataType_TCI
from pcapkit.protocols.data.link.vlan import VLAN as DataType_VLAN
from pcapkit.protocols.link.link import Link

if TYPE_CHECKING:
    from typing import Any, NoReturn, Optional

    from typing_extensions import Literal

    from pcapkit.const.reg.ethertype import EtherType as RegType_EtherType

__all__ = ['VLAN']


class VLAN(Link):
    """This class implements 802.1Q Customer VLAN Tag Type."""

    #: Parsed packet data.
    _info: 'DataType_VLAN'

    ##########################################################################
    # Properties.
    ##########################################################################

    @property
    def name(self) -> 'Literal["802.1Q Customer VLAN Tag Type"]':
        """Name of current protocol."""
        return '802.1Q Customer VLAN Tag Type'

    @property
    def alias(self) -> 'Literal["802.1Q"]':
        """Acronym of corresponding protocol."""
        return '802.1Q'

    @property
    def length(self) -> 'Literal[4]':
        """Header length of current protocol."""
        return 4

    @property
    def protocol(self) -> 'RegType_EtherType':
        """Name of next layer protocol."""
        return self._info.type

    ##########################################################################
    # Methods.
    ##########################################################################

    def read(self, length: 'Optional[int]' = None, **kwargs: 'Any') -> 'DataType_VLAN':  # pylint: disable=unused-argument
        """Read 802.1Q Customer VLAN Tag Type.

        Args:
            length: Length of packet data.

        Keyword Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Parsed packet data.

        """
        if length is None:
            length = len(self)

        _tcif = self._read_binary(2)
        _type = self._read_protos(2)

        vlan = DataType_VLAN(
            tci=DataType_TCI(
                pcp=RegType_PriorityLevel.get(int(_tcif[:3], base=2)),
                dei=bool(_tcif[3]),
                vid=int(_tcif[4:], base=2),
            ),
            type=_type,
        )
        return self._decode_next_layer(vlan, _type, length - self.length)  # type: ignore[return-value]

    def make(self, **kwargs: 'Any') -> 'NoReturn':
        """Make (construct) packet data.

        Keyword Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Constructed packet data.

        """
        raise NotImplementedError

    ##########################################################################
    # Data models.
    ##########################################################################

    def __length_hint__(self) -> 'Literal[4]':
        """Return an estimated length for the object."""
        return 4
