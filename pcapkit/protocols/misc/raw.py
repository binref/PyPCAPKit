# -*- coding: utf-8 -*-
"""raw packet data

:mod:`pcapkit.protocols.raw` contains
:class:`~pcapkit.protocols.raw.Raw` only, which implements
extractor for unknown protocol, and constructs a
:class:`~pcapkit.protocols.protocol.Protocol` like object.

"""
import io
from typing import TYPE_CHECKING, overload

from pcapkit.corekit.protochain import ProtoChain
from pcapkit.protocols.data.misc.raw import Raw as DataType_Raw
from pcapkit.protocols.misc.null import NoPayload
from pcapkit.protocols.protocol import Protocol
from pcapkit.utilities.exceptions import UnsupportedCall

if TYPE_CHECKING:
    from typing import Any, BinaryIO, NoReturn, Optional

    from typing_extensions import Literal

__all__ = ['Raw']


class Raw(Protocol):
    """This class implements universal unknown protocol."""

    #: Parsed packet data.
    _info: 'DataType_Raw'

    ##########################################################################
    # Properties.
    ##########################################################################

    # name of current protocol
    @property
    def name(self) -> 'Literal["Unknown"]':
        """Name of current protocol."""
        return 'Unknown'

    # header length of current protocol
    @property
    def length(self) -> 'NoReturn':
        """Header length of current protocol.

        Raises:
            UnsupportedCall: This protocol doesn't support :attr:`length`.

        """
        raise UnsupportedCall(f"{self.__class__.__name__!r} object has no attribute 'length'")

    # name of next layer protocol
    @property
    def protocol(self) -> 'NoReturn':
        """Name of next layer protocol.

        Raises:
            UnsupportedCall: This protocol doesn't support :attr:`protocol`.

        """
        raise UnsupportedCall(f"{self.__class__.__name__!r} object has no attribute 'protocol'")

    ##########################################################################
    # Methods.
    ##########################################################################

    def read(self, length: 'Optional[int]' = None, *, error: 'Optional[Exception]' = None,  # pylint: disable=arguments-differ
             **kwargs: 'Any') -> 'DataType_Raw':  # pylint: disable=unused-argument
        """Read raw packet data.

        Args:
            length: Length of packet data.

        Keyword Args:
            error: Parsing errors if any.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The parsed packet data.

        """
        raw = DataType_Raw(
            packet=self._data,
            error=error,
        )

        return raw

    def make(self, **kwargs: 'Any') -> 'bytes':
        """Make raw packet data.

        Keyword Args:
            packet (bytes): Raw packet data.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Constructed packet data.

        """
        packet = kwargs.get('packet', b'')
        return packet

    ##########################################################################
    # Data models.
    ##########################################################################

    @overload
    def __post_init__(self, file: 'BinaryIO', length: 'Optional[int]' = ..., **kwargs: 'Any') -> 'None': ...
    @overload
    def __post_init__(self, **kwargs: 'Any') -> 'None': ...  # pylint: disable=arguments-differ

    def __post_init__(self, file: 'Optional[BinaryIO]' = None,
                      length: 'Optional[int]' = None, **kwargs: 'Any') -> 'None':
        """Post initialisation hook.

        Args:
            file: Source packet stream.
            length: Length of packet data.

        Keyword Args:
            error (Optional[Exception]): Parsing errors if any (for parsing).
            **kwargs: Arbitrary keyword arguments.

        Would :mod:`pcapkit` encounter malformed packets, the original parsing
        error instance will be provided as in ``error``.

        See Also:
            For construction argument, please refer to :meth:`make`.

        """
        if file is None:
            _data = self.make(**kwargs)
        else:
            _data = file.read(length)  # type: ignore[arg-type]

        #: bytes: Raw packet data.
        self._data = _data
        #: io.BytesIO: Source packet stream.
        self._file = io.BytesIO(self._data)
        #: pcapkit.protocols.data.misc.raw.Raw: Parsed packet data.
        self._info = self.read(length, **kwargs)

        #: pcapkit.protocols.null.NoPayload: Next layer (no payload).
        self._next = NoPayload()
        #: pcapkit.corekit.protochain.ProtoChain: Protocol chain from current layer.
        self._protos = ProtoChain(self.__class__, self.alias)

    @classmethod
    def __index__(cls) -> 'NoReturn':
        """Numeral registry index of the protocol.

        Raises:
            UnsupportedCall: This protocol has no registry entry.

        """
        raise UnsupportedCall(f'{cls.__name__!r} object cannot be interpreted as an integer')