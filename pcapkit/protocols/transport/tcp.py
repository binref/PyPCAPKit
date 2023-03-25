# -*- coding: utf-8 -*-
"""TCP - Transmission Control Protocol
=========================================

:mod:`pcapkit.protocols.transport.tcp` contains
:class:`~pcapkit.protocols.transport.tcp.TCP` only,
which implements extractor for Transmission Control
Protocol (TCP) [*]_, whose structure is described as
below:

======= ========= ========================= =======================================
Octets      Bits        Name                    Description
======= ========= ========================= =======================================
  0           0   ``tcp.srcport``           Source Port
  2          16   ``tcp.dstport``           Destination Port
  4          32   ``tcp.seq``               Sequence Number
  8          64   ``tcp.ack``               Acknowledgement Number (if ACK set)
  12         96   ``tcp.hdr_len``           Data Offset
  12        100                             Reserved (must be ``\\x00``)
  12        103   ``tcp.flags.ns``          ECN Concealment Protection (NS)
  13        104   ``tcp.flags.cwr``         Congestion Window Reduced (CWR)
  13        105   ``tcp.flags.ece``         ECN-Echo (ECE)
  13        106   ``tcp.flags.urg``         Urgent (URG)
  13        107   ``tcp.flags.ack``         Acknowledgement (ACK)
  13        108   ``tcp.flags.psh``         Push Function (PSH)
  13        109   ``tcp.flags.rst``         Reset Connection (RST)
  13        110   ``tcp.flags.syn``         Synchronize Sequence Numbers (SYN)
  13        111   ``tcp.flags.fin``         Last Packet from Sender (FIN)
  14        112   ``tcp.window_size``       Size of Receive Window
  16        128   ``tcp.checksum``          Checksum
  18        144   ``tcp.urgent_pointer``    Urgent Pointer (if URG set)
  20        160   ``tcp.opt``               TCP Options (if data offset > 5)
======= ========= ========================= =======================================

.. [*] https://en.wikipedia.org/wiki/Transmission_Control_Protocol

"""
import collections
import datetime
import ipaddress
import sys
from typing import TYPE_CHECKING

from pcapkit.const.reg.transtype import TransType
from pcapkit.const.tcp.checksum import Checksum as Enum_Checksum
from pcapkit.const.tcp.mp_tcp_option import MPTCPOption as Enum_MPTCPOption
from pcapkit.const.tcp.option import Option as Enum_Option
from pcapkit.corekit.multidict import OrderedMultiDict
from pcapkit.protocols.data.transport.tcp import CC as Data_CC
from pcapkit.protocols.data.transport.tcp import MPTCPDSS as Data_MPTCPDSS
from pcapkit.protocols.data.transport.tcp import SACK as Data_SACK
from pcapkit.protocols.data.transport.tcp import TCP as Data_TCP
from pcapkit.protocols.data.transport.tcp import AlternateChecksumData as Data_AlternateChecksumData
from pcapkit.protocols.data.transport.tcp import \
    AlternateChecksumRequest as Data_AlternateChecksumRequest
from pcapkit.protocols.data.transport.tcp import Authentication as Data_Authentication
from pcapkit.protocols.data.transport.tcp import CCEcho as Data_CCEcho
from pcapkit.protocols.data.transport.tcp import CCNew as Data_CCNew
from pcapkit.protocols.data.transport.tcp import Echo as Data_Echo
from pcapkit.protocols.data.transport.tcp import EchoReply as Data_EchoReply
from pcapkit.protocols.data.transport.tcp import EndOfOptionList as Data_EndOfOptionList
from pcapkit.protocols.data.transport.tcp import FastOpenCookie as Data_FastOpenCookie
from pcapkit.protocols.data.transport.tcp import Flags as Data_Flags
from pcapkit.protocols.data.transport.tcp import MaximumSegmentSize as Data_MaximumSegmentSize
from pcapkit.protocols.data.transport.tcp import MD5Signature as Data_MD5Signature
from pcapkit.protocols.data.transport.tcp import MPTCPAddAddress as Data_MPTCPAddAddress
from pcapkit.protocols.data.transport.tcp import MPTCPCapable as Data_MPTCPCapable
from pcapkit.protocols.data.transport.tcp import MPTCPCapableFlag as Data_MPTCPCapableFlag
from pcapkit.protocols.data.transport.tcp import MPTCPDSSFlag as Data_MPTCPDSSFlag
from pcapkit.protocols.data.transport.tcp import MPTCPFallback as Data_MPTCPFallback
from pcapkit.protocols.data.transport.tcp import MPTCPFastclose as Data_MPTCPFastclose
from pcapkit.protocols.data.transport.tcp import MPTCPJoinACK as Data_MPTCPJoinACK
from pcapkit.protocols.data.transport.tcp import MPTCPJoinSYN as Data_MPTCPJoinSYN
from pcapkit.protocols.data.transport.tcp import MPTCPJoinSYNACK as Data_MPTCPJoinSYNACK
from pcapkit.protocols.data.transport.tcp import MPTCPPriority as Data_MPTCPPriority
from pcapkit.protocols.data.transport.tcp import MPTCPRemoveAddress as Data_MPTCPRemoveAddress
from pcapkit.protocols.data.transport.tcp import MPTCPUnknown as Data_MPTCPUnknown
from pcapkit.protocols.data.transport.tcp import NoOperation as Data_NoOperation
from pcapkit.protocols.data.transport.tcp import \
    PartialOrderConnectionPermitted as Data_PartialOrderConnectionPermitted
from pcapkit.protocols.data.transport.tcp import \
    PartialOrderConnectionProfile as Data_PartialOrderConnectionProfile
from pcapkit.protocols.data.transport.tcp import QuickStartResponse as Data_QuickStartResponse
from pcapkit.protocols.data.transport.tcp import SACKPermitted as Data_SACKPermitted
from pcapkit.protocols.data.transport.tcp import Timestamp as Data_Timestamp
from pcapkit.protocols.data.transport.tcp import UnassignedOption as Data_UnassignedOption
from pcapkit.protocols.data.transport.tcp import UserTimeout as Data_UserTimeout
from pcapkit.protocols.data.transport.tcp import WindowScale as Data_WindowScale
from pcapkit.protocols.schema.transport.tcp import CC as Schema_CC
from pcapkit.protocols.schema.transport.tcp import MPTCPDSS as Schema_MPTCPDSS
from pcapkit.protocols.schema.transport.tcp import SACK as Schema_SACK
from pcapkit.protocols.schema.transport.tcp import TCP as Schema_TCP
from pcapkit.protocols.schema.transport.tcp import \
    AlternateChecksumData as Schema_AlternateChecksumData
from pcapkit.protocols.schema.transport.tcp import \
    AlternateChecksumRequest as Schema_AlternateChecksumRequest
from pcapkit.protocols.schema.transport.tcp import Authentication as Schema_Authentication
from pcapkit.protocols.schema.transport.tcp import CCEcho as Schema_CCEcho
from pcapkit.protocols.schema.transport.tcp import CCNew as Schema_CCNew
from pcapkit.protocols.schema.transport.tcp import Echo as Schema_Echo
from pcapkit.protocols.schema.transport.tcp import EchoReply as Schema_EchoReply
from pcapkit.protocols.schema.transport.tcp import EndOfOptionList as Schema_EndOfOptionList
from pcapkit.protocols.schema.transport.tcp import FastOpenCookie as Schema_FastOpenCookie
from pcapkit.protocols.schema.transport.tcp import Flags as Schema_Flags
from pcapkit.protocols.schema.transport.tcp import MaximumSegmentSize as Schema_MaximumSegmentSize
from pcapkit.protocols.schema.transport.tcp import MD5Signature as Schema_MD5Signature
from pcapkit.protocols.schema.transport.tcp import MPTCPAddAddress as Schema_MPTCPAddAddress
from pcapkit.protocols.schema.transport.tcp import MPTCPCapable as Schema_MPTCPCapable
from pcapkit.protocols.schema.transport.tcp import MPTCPCapableFlag as Schema_MPTCPCapableFlag
from pcapkit.protocols.schema.transport.tcp import MPTCPDSSFlag as Schema_MPTCPDSSFlag
from pcapkit.protocols.schema.transport.tcp import MPTCPFallback as Schema_MPTCPFallback
from pcapkit.protocols.schema.transport.tcp import MPTCPFastclose as Schema_MPTCPFastclose
from pcapkit.protocols.schema.transport.tcp import MPTCPJoinACK as Schema_MPTCPJoinACK
from pcapkit.protocols.schema.transport.tcp import MPTCPJoinSYN as Schema_MPTCPJoinSYN
from pcapkit.protocols.schema.transport.tcp import MPTCPJoinSYNACK as Schema_MPTCPJoinSYNACK
from pcapkit.protocols.schema.transport.tcp import MPTCPPriority as Schema_MPTCPPriority
from pcapkit.protocols.schema.transport.tcp import MPTCPRemoveAddress as Schema_MPTCPRemoveAddress
from pcapkit.protocols.schema.transport.tcp import MPTCPUnknown as Schema_MPTCPUnknown
from pcapkit.protocols.schema.transport.tcp import NoOperation as Schema_NoOperation
from pcapkit.protocols.schema.transport.tcp import \
    PartialOrderConnectionPermitted as Schema_PartialOrderConnectionPermitted
from pcapkit.protocols.schema.transport.tcp import \
    PartialOrderConnectionProfile as Schema_PartialOrderConnectionProfile
from pcapkit.protocols.schema.transport.tcp import QuickStartResponse as Schema_QuickStartResponse
from pcapkit.protocols.schema.transport.tcp import SACKPermitted as Schema_SACKPermitted
from pcapkit.protocols.schema.transport.tcp import Timestamp as Schema_Timestamp
from pcapkit.protocols.schema.transport.tcp import UnassignedOption as Schema_UnassignedOption
from pcapkit.protocols.schema.transport.tcp import UserTimeout as Schema_UserTimeout
from pcapkit.protocols.schema.transport.tcp import WindowScale as Schema_WindowScale
from pcapkit.protocols.transport.transport import Transport
from pcapkit.utilities.exceptions import ProtocolError
from pcapkit.utilities.warnings import RegistryWarning, warn

if TYPE_CHECKING:
    from typing import Any, Callable, DefaultDict, NoReturn, Optional

    from mypy_extensions import DefaultArg, KwArg, NamedArg
    from typing_extensions import Literal

    from pcapkit.protocols.data.transport.tcp import MPTCP as Data_MPTCP
    from pcapkit.protocols.data.transport.tcp import MPTCPJoin as Data_MPTCPJoin
    from pcapkit.protocols.data.transport.tcp import Option as Data_Option
    from pcapkit.protocols.schema.transport.tcp import MPTCP as Schema_MPTCP
    from pcapkit.protocols.schema.transport.tcp import Option as Schema_Option

    Option = OrderedMultiDict[Enum_Option, Data_Option]
    OptionParser = Callable[['TCP', Enum_Option, NamedArg(Option, 'options')], Data_Option]
    MPOptionParser = Callable[['TCP', Enum_MPTCPOption, int, str, NamedArg(Option, 'options')], Data_MPTCP]
    OptionConstructor = Callable[['TCP', Enum_Option, DefaultArg(Optional[Data_Option]),
                                  KwArg(Any)], Schema_Option]
    MPOptionConstructor = Callable[['TCP', Enum_MPTCPOption, DefaultArg(Optional[Data_MPTCP]),
                                    KwArg(Any)], Schema_MPTCP]

__all__ = ['TCP']


class TCP(Transport[Data_TCP, Schema_TCP],
          schema=Schema_TCP, data=Data_TCP):
    """This class implements Transmission Control Protocol.

    This class currently supports parsing of the following protocols, which are
    registered in the :attr:`self.__proto__ <pcapkit.protocols.transport.tcp.TCP.__proto__>`
    attribute:

    .. list-table::
       :header-rows: 1

       * - Port Number
         - Protocol
       * - 21
         - :class:`pcapkit.protocols.application.ftp.FTP`
       * - 80
         - :class:`pcapkit.protocols.application.http.HTTP`

    This class currently supports parsing of the following TCP options,
    which are directly mapped to the :class:`pcapkit.const.tcp.option.Option`
    enumeration:

    .. list-table::
       :header-rows: 1

       * - Option Code
         - Option Parser
         - Option Constructor
       * - :attr:`~pcapkit.const.tcp.option.Option.End_of_Option_List`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_eool`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_eool`
       * - :attr:`~pcapkit.const.tcp.option.Option.No_Operation`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_nop`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_nop`
       * - :attr:`~pcapkit.const.tcp.option.Option.Maximum_Segment_Size`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_mss`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_mss`
       * - :attr:`~pcapkit.const.tcp.option.Option.Window_Scale`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_ws`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_ws`
       * - :attr:`~pcapkit.const.tcp.option.Option.SACK_Permitted`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_sackpmt`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_sackpmt`
       * - :attr:`~pcapkit.const.tcp.option.Option.SACK`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_sack`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_sack`
       * - :attr:`~pcapkit.const.tcp.option.Option.Echo`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_echo`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_echo`
       * - :attr:`~pcapkit.const.tcp.option.Option.Echo_Reply`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_echore`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_echore`
       * - :attr:`~pcapkit.const.tcp.option.Option.Timestamps`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_ts`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_ts`
       * - :attr:`~pcapkit.const.tcp.option.Option.Partial_Order_Connection_Permitted`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_poc`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_poc`
       * - :attr:`~pcapkit.const.tcp.option.Option.Partial_Order_Service_Profile`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_pocsp`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_pocsp`
       * - :attr:`~pcapkit.const.tcp.option.Option.CC`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_cc`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_cc`
       * - :attr:`~pcapkit.const.tcp.option.Option.CC_NEW`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_ccnew`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_ccnew`
       * - :attr:`~pcapkit.const.tcp.option.Option.CC_ECHO`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_ccecho`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_ccecho`
       * - :attr:`~pcapkit.const.tcp.option.Option.TCP_Alternate_Checksum_Request`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_chkreq`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_chkreq`
       * - :attr:`~pcapkit.const.tcp.option.Option.TCP_Alternate_Checksum_Data`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_chksum`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_chksum`
       * - :attr:`~pcapkit.const.tcp.option.Option.MD5_Signature_Option`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_sig`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_sig`
       * - :attr:`~pcapkit.const.tcp.option.Option.Quick_Start_Response`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_qs`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_qs`
       * - :attr:`~pcapkit.const.tcp.option.Option.User_Timeout_Option`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_timeout`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_timeout`
       * - :attr:`~pcapkit.const.tcp.option.Option.TCP_Authentication_Option`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_ao`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_ao`
       * - :attr:`~pcapkit.const.tcp.option.Option.Multipath_TCP`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_mp`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_mp`
       * - :attr:`~pcapkit.const.tcp.option.Option.TCP_Fast_Open_Cookie`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mode_fastopen`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mode_fastopen`

    This class currently supports parsing of the following Multipath TCP options,
    which are directly mapped to the :class:`pcapkit.const.tcp.mp_tcp_option.MPTCPOption`
    enumeration:

    .. list-table::
       :header-rows: 1

       * - Option Code
         - Option Parser
         - Option Constructor
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.MP_CAPABLE`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_capable`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_capable`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.MP_JOIN`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_join`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_join`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.DSS`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_dss`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_dss`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.ADD_ADDR`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_addaddr`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_addaddr`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.REMOVE_ADDR`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_remove`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_remove`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.MP_PRIO`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_prio`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_prio`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.MP_FAIL`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_fail`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_fail`
       * - :attr:`~pcapkit.const.tcp.mp_tcp_option.MPTCPOption.MP_FASTCLOSE`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._read_mptcp_fastclose`
         - :meth:`~pcapkit.protocols.transport.tcp.TCP._make_mptcp_fastclose`

    """

    ##########################################################################
    # Defaults.
    ##########################################################################

    #: DefaultDict[int, tuple[str, str]]: Protocol index mapping for decoding next layer,
    #: c.f. :meth:`self._decode_next_layer <pcapkit.protocols.transport.transport.Transport._decode_next_layer>`
    #: & :meth:`self._import_next_layer <pcapkit.protocols.protocol.Protocol._import_next_layer>`.
    __proto__ = collections.defaultdict(
        lambda: ('pcapkit.protocols.misc.raw', 'Raw'),
        {
            21: ('pcapkit.protocols.application.ftp', 'FTP'),    # FTP
            80: ('pcapkit.protocols.application.http', 'HTTP'),  # HTTP
        },
    )

    #: DefaultDict[Enum_Option, str | tuple[OptionParser, OptionConstructor]]:
    #: Option code to method mapping, c.f. :meth:`_read_tcp_options` and
    #: :meth:`_make_tcp_options`. Method names are expected to be referred to
    #: the class by ``_read_mode_${name}`` and ``_make_mode_${name}``, and if
    #: such name not found, the value should then be a method that can parse
    #: the option by itself.
    __option__ = collections.defaultdict(
        lambda: 'donone',
        {
            Enum_Option.End_of_Option_List: 'eool',                 # [RFC 793] End of Option List
            Enum_Option.No_Operation: 'nop',                        # [RFC 793] No-Operation
            Enum_Option.Maximum_Segment_Size: 'mss',                # [RFC 793] Maximum Segment Size
            Enum_Option.Window_Scale: 'ws',                         # [RFC 7323] Window Scale
            Enum_Option.SACK_Permitted: 'sackpmt',                  # [RFC 2018] SACK Permitted
            Enum_Option.SACK: 'sack',                               # [RFC 2018] SACK
            Enum_Option.Echo: 'echo',                               # [RFC 1072] Echo
            Enum_Option.Echo_Reply: 'echore',                       # [RFC 1072] Echo Reply
            Enum_Option.Timestamps: 'ts',                           # [RFC 7323] Timestamps
            Enum_Option.Partial_Order_Connection_Permitted: 'poc',  # [RFC 1693] POC Permitted
            Enum_Option.Partial_Order_Service_Profile: 'pocsp',     # [RFC 1693] POC-Serv Profile
            Enum_Option.CC: 'cc',                                   # [RFC 1644] Connection Count
            Enum_Option.CC_NEW: 'ccnew',                            # [RFC 1644] CC.NEW
            Enum_Option.CC_ECHO: 'ccecho',                          # [RFC 1644] CC.ECHO
            Enum_Option.TCP_Alternate_Checksum_Request: 'chkreq',   # [RFC 1146] Alt-Chksum Request
            Enum_Option.TCP_Alternate_Checksum_Data: 'chksum',      # [RFC 1146] Alt-Chksum Data
            Enum_Option.MD5_Signature_Option: 'sig',                # [RFC 2385] MD5 Signature Option
            Enum_Option.Quick_Start_Response: 'qs',                 # [RFC 4782] Quick-Start Response
            Enum_Option.User_Timeout_Option: 'timeout',             # [RFC 5482] User Timeout Option
            Enum_Option.TCP_Authentication_Option: 'ao',            # [RFC 5925] TCP Authentication Option
            Enum_Option.Multipath_TCP: 'mp',                        # [RFC 6824] Multipath TCP
            Enum_Option.TCP_Fast_Open_Cookie: 'fastopen',           # [RFC 7413] Fast Open
        },
    )  # type: DefaultDict[int, str | tuple[OptionParser, OptionConstructor]]

    #: DefaultDict[Enum_MPTCPOption, str | tuple[MPOptionParser, MPOptionConstructor]]:
    #: Option code to method mapping, c.f. :meth:`_read_mode_mp` and :meth:`_make_mode_mp`.
    #: Method names are expected to be referred to the class by ``_read_mptcp_${name}``
    #: and ``_make_mptcp_${name}``, and if such name not found, the value should
    #: then be a method that can parse the option by itself.
    __mp_option__ = collections.defaultdict(
        lambda: 'unknown',
        {
            Enum_MPTCPOption.MP_CAPABLE: 'capable',
            Enum_MPTCPOption.MP_JOIN: 'join',
            Enum_MPTCPOption.DSS: 'dss',
            Enum_MPTCPOption.ADD_ADDR: 'addaddr',
            Enum_MPTCPOption.REMOVE_ADDR: 'removeaddr',
            Enum_MPTCPOption.MP_PRIO: 'prio',
            Enum_MPTCPOption.MP_FAIL: 'fail',
            Enum_MPTCPOption.MP_FASTCLOSE: 'fastclose',
        },
    )  # type: DefaultDict[int, str | tuple[MPOptionParser, MPOptionConstructor]]

    ##########################################################################
    # Properties.
    ##########################################################################

    @property
    def name(self) -> 'Literal["Transmission Control Protocol"]':
        """Name of current protocol."""
        return 'Transmission Control Protocol'

    @property
    def length(self) -> 'int':
        """Header length of current protocol."""
        return self._info.hdr_len

    @property
    def src(self) -> 'int':
        """Source port."""
        return self._info.srcport

    @property
    def dst(self) -> 'int':
        """Destination port."""
        return self._info.dstport

    ##########################################################################
    # Methods.
    ##########################################################################

    def read(self, length: 'Optional[int]' = None, **kwargs: 'Any') -> 'Data_TCP':  # pylint: disable=unused-argument
        """Read Transmission Control Protocol (TCP).

        Structure of TCP header [:rfc:`793`]::

             0                   1                   2                   3
             0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |          Source Port          |       Destination Port        |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |                        Sequence Number                        |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |                   Acknowledgement Number                      |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |  Data |           |U|A|P|R|S|F|                               |
            | Offset| Reserved  |R|C|S|S|Y|I|            Window             |
            |       |           |G|K|H|T|N|N|                               |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |           Checksum            |         Urgent Pointer        |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |                    Options                    |    Padding    |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
            |                             data                              |
            +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

        Args:
            length: Length of packet data.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Parsed packet data.

        """
        if length is None:
            length = len(self)

        _srcp = self._read_unpack(2)
        _dstp = self._read_unpack(2)
        _seqn = self._read_unpack(4)
        _ackn = self._read_unpack(4)
        _lenf = self._read_binary(1)
        _flag = self._read_binary(1)
        _wins = self._read_unpack(2)
        _csum = self._read_fileng(2)
        _urgp = self._read_unpack(2)

        tcp = Data_TCP(
            srcport=_srcp,
            dstport=_dstp,
            seq=_seqn,
            ack=_ackn,
            hdr_len=int(_lenf[:4], base=2) * 4,
            flags=Data_Flags(
                ns=bool(int(_lenf[7])),
                cwr=bool(int(_flag[0])),
                ece=bool(int(_flag[1])),
                urg=bool(int(_flag[2])),
                ack=bool(int(_flag[3])),
                psh=bool(int(_flag[4])),
                rst=bool(int(_flag[5])),
                syn=bool(int(_flag[6])),
                fin=bool(int(_flag[7])),
            ),
            window_size=_wins,
            checksum=_csum,
            urgent_pointer=_urgp,
        )

        # packet type flags
        self._syn = tcp.flags.syn
        self._ack = tcp.flags.ack
        self._fin = tcp.flags.fin

        _optl = tcp.hdr_len - 20
        if _optl:
            tcp.__update__({
                'options': self._read_tcp_options(_optl),
            })

        return self._decode_next_layer(tcp, (tcp.srcport, tcp.dstport), length - tcp.hdr_len)

    def make(self, **kwargs: 'Any') -> 'NoReturn':
        """Make (construct) packet data.

        Args:
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Constructed packet data.

        """
        raise NotImplementedError

    @classmethod
    def register_option(cls, code: 'Enum_Option', meth: 'str | tuple[OptionParser, OptionConstructor]') -> 'None':
        """Register an option parser.

        Args:
            code: TCP option code.
            meth: Method name or callable to parse and/or construct the option.

        """
        if code in cls.__option__:
            warn(f'option {code} already registered, overwriting', RegistryWarning)
        cls.__option__[code] = meth

    @classmethod
    def register_mp_option(cls, code: 'Enum_MPTCPOption', meth: 'str | tuple[MPOptionParser, MPOptionConstructor]') -> 'None':
        """Register an MPTCP option parser.

        Args:
            code: MPTCP option code.
            meth: Method name or callable to parse and/or construct the option.

        """
        if code in cls.__mp_option__:
            warn(f'option {code} already registered, overwriting', RegistryWarning)
        cls.__mp_option__[code] = meth

    ##########################################################################
    # Data models.
    ##########################################################################

    def __length_hint__(self) -> 'Literal[20]':
        """Return an estimated length for the object."""
        return 20

    @classmethod
    def __index__(cls) -> 'TransType':  # pylint: disable=invalid-index-returned
        """Numeral registry index of the protocol.

        Returns:
            Numeral registry index of the protocol in `IANA`_.

        .. _IANA: https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml

        """
        return TransType.TCP  # type: ignore[return-value]

    ##########################################################################
    # Utilities.
    ##########################################################################

    def _read_tcp_options(self, size: 'int') -> 'Option':
        """Read TCP option list.

        Arguments:
            size: length of option list

        Returns:
            Extracted TCP options.

        Raises:
            ProtocolError: If the threshold is **NOT** matching.

        """
        # length of read option list
        counter = 0
        # dict of option data
        options = OrderedMultiDict()  # type: Option

        while counter < size:
            # get option kind
            code = self._read_unpack(1)
            if not code:
                break

            # fetch corresponding option
            kind = Enum_Option.get(code)

            # extract option data
            name = self.__option__[code]  # type: str | OptionParser
            if isinstance(name, str):
                meth_name = f'_read_mode_{name}'
                meth = getattr(
                    self, meth_name,
                    self._read_mode_donone
                )  # type: Callable[[Enum_Option, NamedArg(Option, 'options')], Data_Option]
                data = meth(kind, options=options)  # type: Data_Option
            else:
                data = name(self, kind, options=options)

            # record option data
            counter += data.length
            options.add(kind, data)

            # break when eol triggered
            if kind == Enum_Option.End_of_Option_List:
                break

        # get padding
        if counter < size:
            plen = size - counter
            self._read_fileng(plen)

        return options

    def _read_mode_donone(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_UnassignedOption':  # pylint: disable=unused-argument
        """Read options request no process.

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        size = self._read_unpack(1)
        data = self._read_fileng(size - 2)

        option = Data_UnassignedOption(
            kind=kind,
            length=size,
            data=data,
        )
        return option

    def _read_mode_eool(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_EndOfOptionList':  # pylint: disable=unused-argument
        """Read TCP End of Option List option.

        Structure of TCP end of option list option [:rfc:`793`]:

        .. code-block:: text

           +--------+
           |00000000|
           +--------+
            Kind=0

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        return Data_EndOfOptionList(
            kind=kind,
            length=1,
        )

    def _read_mode_nop(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_NoOperation':  # pylint: disable=unused-argument
        """Read TCP No Operation option.

        Structure of TCP maximum segment size option [:rfc:`793`]:

        .. code-block:: text

           +--------+
           |00000001|
           +--------+
            Kind=1

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        return Data_NoOperation(
            kind=kind,
            length=1,
        )

    def _read_mode_mss(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_MaximumSegmentSize':  # pylint: disable=unused-argument
        """Read TCP max segment size option.

        Structure of TCP maximum segment size option [:rfc:`793`]:

        .. code-block:: text

           +--------+--------+---------+--------+
           |00000010|00000100|   max seg size   |
           +--------+--------+---------+--------+
            Kind=2   Length=4

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``4``.

        """
        size = self._read_unpack(1)
        if size != 4:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        mss = self._read_unpack(size - 2)

        data = Data_MaximumSegmentSize(
            kind=kind,
            length=size,
            mss=mss,
        )
        return data

    def _read_mode_ws(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_WindowScale':  # pylint: disable=unused-argument
        """Read TCP windows scale option.

        Structure of TCP window scale option [:rfc:`7323`]:

        .. code-block:: text

           +---------+---------+---------+
           | Kind=3  |Length=3 |shift.cnt|
           +---------+---------+---------+
                1         1         1

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``3``.

        """
        size = self._read_unpack(1)
        if size != 3:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        scnt = self._read_unpack(size - 2)

        data = Data_WindowScale(
            kind=kind,
            length=size,
            shift=scnt,
        )
        return data

    def _read_mode_sackpmt(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_SACKPermitted':  # pylint: disable=unused-argument
        """Read TCP SACK permitted option.

        Structure of TCP SACK permitted option [:rfc:`2018`]:

        .. code-block:: text

           +---------+---------+
           | Kind=4  | Length=2|
           +---------+---------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``2``.

        """
        size = self._read_unpack(1)
        if size != 2:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        return Data_SACKPermitted(
            kind=kind,
            length=size,
        )

    def _read_mode_sack(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_SACK':  # pylint: disable=unused-argument
        """Read TCP SACK option.

        Structure of TCP SACK option [:rfc:`2018`]:

        .. code-block:: text

                             +--------+--------+
                             | Kind=5 | Length |
           +--------+--------+--------+--------+
           |      Left Edge of 1st Block       |
           +--------+--------+--------+--------+
           |      Right Edge of 1st Block      |
           +--------+--------+--------+--------+
           |                                   |
           /            . . .                  /
           |                                   |
           +--------+--------+--------+--------+
           |      Left Edge of nth Block       |
           +--------+--------+--------+--------+
           |      Right Edge of nth Block      |
           +--------+--------+--------+--------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``8``.

        """
        size = self._read_unpack(1)
        sack = []  # type: list[int]

        for _ in range(size):
            sack.append(self._read_unpack(8))

        data = Data_SACK(
            kind=kind,
            length=size * 8 + 2,
            sack=tuple(sack),
        )
        return data

    def _read_mode_echo(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_Echo':  # pylint: disable=unused-argument
        """Read TCP echo option.

        Structure of TCP echo option [:rfc:`1072`]:

        .. code-block:: text

           +--------+--------+--------+--------+--------+--------+
           | Kind=6 | Length |   4 bytes of info to be echoed    |
           +--------+--------+--------+--------+--------+--------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``6``.

        """
        size = self._read_unpack(1)
        if size != 6:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        echo = self._read_fileng(4)

        data = Data_Echo(
            kind=kind,
            length=size,
            data=echo,
        )
        return data

    def _read_mode_echore(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_EchoReply':  # pylint: disable=unused-argument
        """Read TCP echo reply option.

        Structure of TCP echo reply option [:rfc:`1072`]:

        .. code-block:: text

           +--------+--------+--------+--------+--------+--------+
           | Kind=7 | Length |    4 bytes of echoed info         |
           +--------+--------+--------+--------+--------+--------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``6``.

        """
        size = self._read_unpack(1)
        if size != 6:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        echo = self._read_fileng(4)

        data = Data_EchoReply(
            kind=kind,
            length=size,
            data=echo,
        )
        return data

    def _read_mode_ts(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_Timestamp':  # pylint: disable=unused-argument
        """Read TCP timestamps option.

        Structure of TCP timestamp option [:rfc:`7323`]:

        .. code-block:: text

           +-------+-------+---------------------+---------------------+
           |Kind=8 |  10   |   TS Value (TSval)  |TS Echo Reply (TSecr)|
           +-------+-------+---------------------+---------------------+
               1       1              4                     4

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``10``.

        """
        size = self._read_unpack(1)
        if size != 10:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        tsval = self._read_unpack(4)
        tsecr = self._read_fileng(4)

        data = Data_Timestamp(
            kind=kind,
            length=size,
            timestamp=tsval,
            echo=tsecr,
        )
        return data

    def _read_mode_poc(self, kind: 'Enum_Option', *,
                       options: 'Option') -> 'Data_PartialOrderConnectionPermitted':  # pylint: disable=unused-argument
        """Read TCP partial order connection service profile option.

        Structure of TCP ``POC-Permitted`` option [:rfc:`1693`][:rfc:`6247`]:

        .. code-block:: text

           +-----------+-------------+
           |  Kind=9   |  Length=2   |
           +-----------+-------------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``2``.

        """
        size = self._read_unpack(1)
        if size != 2:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        return Data_PartialOrderConnectionPermitted(
            kind=kind,
            length=size,
        )

    def _read_mode_pocsp(self, kind: 'Enum_Option', *,
                         options: 'Option') -> 'Data_PartialOrderConnectionProfile':  # pylint: disable=unused-argument
        """Read TCP partial order connection service profile option.

        Structure of TCP ``POC-SP`` option [:rfc:`1693`][:rfc:`6247`]:

        .. code-block:: text

                                     1 bit        1 bit    6 bits
           +----------+----------+------------+----------+--------+
           |  Kind=10 | Length=3 | Start_flag | End_flag | Filler |
           +----------+----------+------------+----------+--------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``3``.

        """
        size = self._read_unpack(1)
        if size != 3:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        temp = self._read_binary(size)

        data = Data_PartialOrderConnectionProfile(
            kind=kind,
            length=size,
            start=bool(int(temp[0])),
            end=bool(int(temp[1])),
        )

        return data

    def _read_mode_cc(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_CC':  # pylint: disable=unused-argument
        """Read TCP connection count option.

        Structure of TCP ``CC`` option [:rfc:`1644`]:

        .. code-block:: text

           +--------+--------+--------+--------+--------+--------+
           |00001011|00000110|    Connection Count:  SEG.CC      |
           +--------+--------+--------+--------+--------+--------+
            Kind=11  Length=6

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``6``.

        """
        size = self._read_unpack(1)
        if size != 6:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        cc = self._read_unpack(4)

        data = Data_CC(
            kind=kind,
            length=size,
            cc=cc,
        )
        return data

    def _read_mode_ccnew(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_CCNew':  # pylint: disable=unused-argument
        """Read TCP connection count (new) option.

        Structure of TCP ``CC.NEW`` option [:rfc:`1644`]:

        .. code-block:: text

           +--------+--------+--------+--------+--------+--------+
           |00001100|00000110|    Connection Count:  SEG.CC      |
           +--------+--------+--------+--------+--------+--------+
            Kind=12  Length=6

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``6``.

        """
        size = self._read_unpack(1)
        if size != 6:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        cc = self._read_unpack(4)

        data = Data_CCNew(
            kind=kind,
            length=size,
            cc=cc,
        )
        return data

    def _read_mode_ccecho(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_CCEcho':  # pylint: disable=unused-argument
        """Read TCP connection count (echo) option.

        Structure of TCP ``CC.ECHO`` option [:rfc:`1644`]:

        .. code-block:: text

           +--------+--------+--------+--------+--------+--------+
           |00001101|00000110|    Connection Count:  SEG.CC      |
           +--------+--------+--------+--------+--------+--------+
            Kind=13  Length=6

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``6``.

        """
        size = self._read_unpack(1)
        if size != 6:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        cc = self._read_unpack(4)

        data = Data_CCEcho(
            kind=kind,
            length=size,
            cc=cc,
        )
        return data

    def _read_mode_chkreq(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_AlternateChecksumRequest':  # pylint: disable=unused-argument
        """Read Alternate Checksum Request option.

        Structure of TCP ``CHKSUM-REQ`` [:rfc:`1146`][:rfc:`6247`]:

        .. code-block:: text

           +----------+----------+----------+
           |  Kind=14 | Length=3 |  chksum  |
           +----------+----------+----------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``3``.

        """
        size = self._read_unpack(1)
        if size != 3:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        algo = Enum_Checksum.get(self._read_unpack(1))

        data = Data_AlternateChecksumRequest(
            kind=kind,
            length=size,
            chksum=algo,
        )

        return data

    def _read_mode_chksum(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_AlternateChecksumData':  # pylint: disable=unused-argument
        """Read Alternate Checksum Data option.

        Structure of TCP ``CHKSUM`` [:rfc:`1146`][:rfc:`6247`]:

        .. code-block:: text

           +---------+---------+---------+     +---------+
           | Kind=15 |Length=N |  data   | ... |  data   |
           +---------+---------+---------+     +---------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        size = self._read_unpack(1)
        csum = self._read_fileng(size - 2)

        data = Data_AlternateChecksumData(
            kind=kind,
            length=size,
            data=csum,
        )

        return data

    def _read_mode_sig(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_MD5Signature':  # pylint: disable=unused-argument
        """Read MD5 Signature option.

        Structure of TCP ``SIG`` option [:rfc:`2385`]:

        .. code-block:: text

           +---------+---------+-------------------+
           | Kind=19 |Length=18|   MD5 digest...   |
           +---------+---------+-------------------+
           |                                       |
           +---------------------------------------+
           |                                       |
           +---------------------------------------+
           |                                       |
           +-------------------+-------------------+
           |                   |
           +-------------------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``18``.

        """
        size = self._read_unpack(1)
        if size != 18:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        sig = self._read_fileng(16)

        data = Data_MD5Signature(
            kind=kind,
            length=size,
            digest=sig,
        )
        return data

    def _read_mode_qs(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_QuickStartResponse':  # pylint: disable=unused-argument
        """Read Quick-Start Response option.

        Structure of TCP ``QSopt`` [:rfc:`4782`]:

        .. code-block:: text

            0                   1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |     Kind      |  Length=8     | Resv. | Rate  |   TTL Diff    |
           |               |               |       |Request|               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                   QS Nonce                                | R |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``8``.

        """
        size = self._read_unpack(1)
        if size != 8:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        rvrr = self._read_binary(1)
        ttld = self._read_unpack(1)
        noun = self._read_binary(4)

        data = Data_QuickStartResponse(
            kind=kind,
            length=size,
            req_rate=int(rvrr[4:], base=2),
            ttl_diff=ttld,
            nonce=int(noun[:-2], base=2),
        )

        return data

    def _read_mode_timeout(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_UserTimeout':  # pylint: disable=unused-argument
        """Read User Timeout option.

        Structure of TCP ``TIMEOUT`` [:rfc:`5482`]:

        .. code-block:: text

            0                   1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |   Kind = 28   |   Length = 4  |G|        User Timeout         |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``4``.

        """
        size = self._read_unpack(1)
        if size != 4:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        temp = self._read_binary(size)
        if temp[0] == '1':
            time = datetime.timedelta(minutes=int(temp[0:], base=2))
        else:
            time = datetime.timedelta(seconds=int(temp[0:], base=2))

        data = Data_UserTimeout(
            kind=kind,
            length=size,
            timeout=time,
        )

        return data

    def _read_mode_ao(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_Authentication':  # pylint: disable=unused-argument
        """Read Authentication option.

        Structure of TCP ``AOopt`` [:rfc:`5925`]:

        .. code-block:: text

           +------------+------------+------------+------------+
           |  Kind=29   |   Length   |   KeyID    | RNextKeyID |
           +------------+------------+------------+------------+
           |                     MAC           ...
           +-----------------------------------...

           ...-----------------+
           ...  MAC (con't)    |
           ...-----------------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** larger than or equal to ``4``.

        """
        size = self._read_unpack(1)
        if size < 4:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        key_ = self._read_unpack(1)
        rkey = self._read_unpack(1)
        mac_ = self._read_fileng(size - 4)

        data = Data_Authentication(
            kind=kind,
            length=size,
            key_id=key_,
            next_key_id=rkey,
            mac=mac_,
        )

        return data

    def _read_mode_mp(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_MPTCP':  # pylint: disable=unused-argument
        """Read Multipath TCP option.

        Structure of ``MP-TCP`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-----------------------+
           |     Kind      |    Length     |Subtype|                       |
           +---------------+---------------+-------+                       |
           |                     Subtype-specific data                     |
           |                       (variable length)                       |
           +---------------------------------------------------------------+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        size = self._read_unpack(1)
        bins = self._read_binary(1)
        subt = int(bins[:4], base=2)    # subtype number
        bits = bins[4:]                 # 4-bit data
        dlen = size - 3                 # length of remaining data

        # fetch subtype-specific data
        subtype = Enum_MPTCPOption.get(subt)
        name = self.__mp_option__[subt]  # type: str | MPOptionParser
        if isinstance(name, str):
            meth_name = f'_read_mptcp_{name}'
            meth = getattr(
                self, meth_name,
                self._read_mptcp_unknown
            )  # type: Callable[[Enum_MPTCPOption, int, str, NamedArg(Option, 'options')], Data_MPTCP]
            data = meth(subtype, dlen, bits, options=options)
        else:
            data = name(self, subtype, dlen, bits, options=options)

        return data

    def _read_mptcp_unknown(self, kind: 'Enum_MPTCPOption', dlen: int,
                            bits: str, *, options: 'Option') -> 'Data_MPTCPUnknown':  # pylint: disable=unused-argument
        """Read unknown MPTCP subtype.

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        data = Data_MPTCPUnknown(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            data=int(bits[:4], base=2).to_bytes(1, sys.byteorder) + self._read_fileng(dlen),
        )
        return data

    def _read_mptcp_capable(self, kind: 'Enum_MPTCPOption', dlen: int,
                            bits: str, *, options: 'Option') -> 'Data_MPTCPCapable':  # pylint: disable=unused-argument
        """Read Multipath Capable option.

        Structure of ``MP_CAPABLE`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-------+---------------+
           |     Kind      |    Length     |Subtype|Version|A|B|C|D|E|F|G|H|
           +---------------+---------------+-------+-------+---------------+
           |                   Option Sender's Key (64 bits)               |
           |                                                               |
           |                                                               |
           +---------------------------------------------------------------+
           |                  Option Receiver's Key (64 bits)              |
           |                     (if option Length == 20)                  |
           |                                                               |
           +---------------------------------------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``20`` or ``32``.

        """
        if dlen not in (17, 29):
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        vers = int(bits, base=2)
        bins = self._read_binary(1)
        skey = self._read_unpack(8)
        rkey = self._read_unpack(8) if dlen == 17 else None

        data = Data_MPTCPCapable(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            version=vers,
            flags=Data_MPTCPCapableFlag(
                req=bool(int(bins[0])),
                ext=bool(int(bins[1])),
                hsa=bool(int(bins[7])),
            ),
            skey=skey,
            rkey=rkey,
        )

        return data

    def _read_mptcp_join(self, kind: 'Enum_MPTCPOption', dlen: int,
                         bits: str, *, options: 'Option') -> 'Data_MPTCPJoin':
        """Read Join Connection option.

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If the option is not given on a valid SYN/ACK packet.

        """
        if self._syn and not self._ack:  # MP_JOIN-SYN
            return self._read_join_syn(kind, dlen, bits, options=options)
        if self._syn and self._ack:      # MP_JOIN-SYN/ACK
            return self._read_join_synack(kind, dlen, bits, options=options)
        if not self._syn and self._ack:  # MP_JOIN-ACK
            return self._read_join_ack(kind, dlen, bits, options=options)
        raise ProtocolError(f'{self.alias}: : [OptNo {kind.value}] invalid flags combination')

    def _read_join_syn(self, kind: 'Enum_MPTCPOption', dlen: int,
                       bits: str, *, options: 'Option') -> 'Data_MPTCPJoinSYN':  # pylint: disable=unused-argument
        """Read Join Connection option for Initial SYN.

        Structure of ``MP_JOIN-SYN`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-----+-+---------------+
           |     Kind      |  Length = 12  |Subtype|     |B|   Address ID  |
           +---------------+---------------+-------+-----+-+---------------+
           |                   Receiver's Token (32 bits)                  |
           +---------------------------------------------------------------+
           |                Sender's Random Number (32 bits)               |
           +---------------------------------------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``12``.

        """
        if dlen != 9:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        adid = self._read_unpack(1)
        rtkn = self._read_fileng(4)
        srno = self._read_unpack(4)

        data = Data_MPTCPJoinSYN(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            connection='SYN',
            backup=bool(int(bits[3])),
            addr_id=adid,
            token=rtkn,
            nonce=srno,
        )

        return data

    def _read_join_synack(self, kind: 'Enum_MPTCPOption', dlen: int,
                          bits: str, *, options: 'Option') -> 'Data_MPTCPJoinSYNACK':  # pylint: disable=unused-argument
        """Read Join Connection option for Responding SYN/ACK.

        Structure of ``MP_JOIN-SYN/ACK`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-----+-+---------------+
           |     Kind      |  Length = 16  |Subtype|     |B|   Address ID  |
           +---------------+---------------+-------+-----+-+---------------+
           |                                                               |
           |                Sender's Truncated HMAC (64 bits)              |
           |                                                               |
           +---------------------------------------------------------------+
           |                Sender's Random Number (32 bits)               |
           +---------------------------------------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``20``.

        """
        if dlen != 17:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        adid = self._read_unpack(1)
        hmac = self._read_fileng(8)
        srno = self._read_unpack(4)

        data = Data_MPTCPJoinSYNACK(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            connection='SYN/ACK',
            backup=bool(int(bits[3])),
            addr_id=adid,
            hmac=hmac,
            nonce=srno,
        )

        return data

    def _read_join_ack(self, kind: 'Enum_MPTCPOption', dlen: int,
                       bits: str, *, options: 'Option') -> 'Data_MPTCPJoinACK':  # pylint: disable=unused-argument
        """Read Join Connection option for Third ACK.

        Structure of ``MP_JOIN-ACK`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-----------------------+
           |     Kind      |  Length = 24  |Subtype|      (reserved)       |
           +---------------+---------------+-------+-----------------------+
           |                                                               |
           |                                                               |
           |                   Sender's HMAC (160 bits)                    |
           |                                                               |
           |                                                               |
           +---------------------------------------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** ``24``.

        """
        if dlen != 21:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        temp = self._read_fileng(20)

        data = Data_MPTCPJoinACK(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            connection='ACK',
            hmac=temp,
        )

        return data

    def _read_mptcp_dss(self, kind: 'Enum_MPTCPOption', dlen: int,
                        bits: str, *, options: 'Option') -> 'Data_MPTCPDSS':  # pylint: disable=unused-argument
        """Read Data Sequence Signal (Data ACK and Data Sequence Mapping) option.

        Structure of ``DSS`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+----------------------+
           |     Kind      |    Length     |Subtype| (reserved) |F|m|M|a|A|
           +---------------+---------------+-------+----------------------+
           |                                                              |
           |           Data ACK (4 or 8 octets, depending on flags)       |
           |                                                              |
           +--------------------------------------------------------------+
           |                                                              |
           |   Data sequence number (4 or 8 octets, depending on flags)   |
           |                                                              |
           +--------------------------------------------------------------+
           |              Subflow Sequence Number (4 octets)              |
           +-------------------------------+------------------------------+
           |  Data-Level Length (2 octets) |      Checksum (2 octets)     |
           +-------------------------------+------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        """
        flag = self._read_binary(1)
        mflg = 8 if int(flag[4]) else 4
        Mflg = bool(int(flag[5]))
        aflg = 8 if int(flag[6]) else 4
        Aflg = bool(int(flag[7]))
        ack_ = self._read_unpack(aflg) if Aflg else None
        dsn_ = self._read_unpack(mflg) if Mflg else None
        ssn_ = self._read_unpack(4) if Mflg else None
        dll_ = self._read_unpack(2) if Mflg else None
        chk_ = self._read_fileng(2) if Mflg else None

        data = Data_MPTCPDSS(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            flags=Data_MPTCPDSSFlag(
                data_fin=bool(int(flag[3])),
                dsn_oct=bool(int(flag[4])),
                data_pre=Mflg,
                ack_oct=bool(int(flag[6])),
                ack_pre=Aflg,
            ),
            ack=ack_,
            dsn=dsn_,
            ssn=ssn_,
            dl_len=dll_,
            checksum=chk_,
        )

        return data

    def _read_mptcp_addaddr(self, kind: 'Enum_MPTCPOption', dlen: int,
                            bits: str, *, options: 'Option') -> 'Data_MPTCPAddAddress':  # pylint: disable=unused-argument
        """Read Add Address option.

        Structure of ``ADD_ADDR`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-------+---------------+
           |     Kind      |     Length    |Subtype| IPVer |  Address ID   |
           +---------------+---------------+-------+-------+---------------+
           |          Address (IPv4 - 4 octets / IPv6 - 16 octets)         |
           +-------------------------------+-------------------------------+
           |   Port (2 octets, optional)   |
           +-------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: Invalid IP version and/or addresses.

        """
        vers = int(bits, base=2)
        if vers == 4:
            ip_l = 4
        elif vers == 6:
            ip_l = 16
        else:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        adid = self._read_unpack(1)
        ipad = self._read_fileng(ip_l)
        pt_l = dlen - 1 - ip_l
        port = self._read_unpack(2) if pt_l else None

        data = Data_MPTCPAddAddress(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            version=vers,
            addr_id=adid,
            addr=ipaddress.ip_address(ipad),
            port=port,
        )

        return data

    def _read_mptcp_remove(self, kind: 'Enum_MPTCPOption', dlen: int,
                           bits: str, *, options: 'Option') -> 'Data_MPTCPRemoveAddress':  # pylint: disable=unused-argument
        """Read Remove Address option.

        Structure of ``REMOVE_ADDR`` [:rfc:`6824`]:

        .. code-block:: text

                                 1                   2                   3
             0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
            +---------------+---------------+-------+-------+---------------+
            |     Kind      |  Length = 3+n |Subtype|(resvd)|   Address ID  | ...
            +---------------+---------------+-------+-------+---------------+
                                       (followed by n-1 Address IDs, if required)

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If the length is smaller than **3**.

        """
        if dlen <= 0:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        adid = []  # type: list[int]
        for _ in range(dlen):
            adid.append(self._read_unpack(1))

        data = Data_MPTCPRemoveAddress(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            addr_id=tuple(adid),
        )

        return data

    def _read_mptcp_prio(self, kind: 'Enum_MPTCPOption', dlen: int,
                         bits: str, *, options: 'Option') -> 'Data_MPTCPPriority':  # pylint: disable=unused-argument
        """Read Change Subflow Priority option.

        Structure of ``MP_PRIO`` [RFC 6824]:

        .. code-block:: text

                                 1                   2                   3
             0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-----+-+--------------+
           |     Kind      |     Length    |Subtype|     |B| AddrID (opt) |
           +---------------+---------------+-------+-----+-+--------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If the length is smaller than **3**.

        """
        if dlen < 0:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        temp = self._read_unpack(1) if dlen else None

        data = Data_MPTCPPriority(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            backup=bool(int(bits[3])),
            addr_id=temp,
        )

        return data

    def _read_mptcp_fail(self, kind: 'Enum_MPTCPOption', dlen: int,
                         bits: str, *, options: 'Option') -> 'Data_MPTCPFallback':  # pylint: disable=unused-argument
        """Read Fallback option.

        Structure of ``MP_FAIL`` [:rfc:`6824`]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+----------------------+
           |     Kind      |   Length=12   |Subtype|      (reserved)      |
           +---------------+---------------+-------+----------------------+
           |                                                              |
           |                 Data Sequence Number (8 octets)              |
           |                                                              |
           +--------------------------------------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If the length is **NOT** 12.

        """
        if dlen != 9:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        resv = self._read_fileng(1)  # pylint: disable=unused-variable
        dsn_ = self._read_unpack(8)

        data = Data_MPTCPFallback(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            dsn=dsn_,
        )

        return data

    def _read_mptcp_fastclose(self, kind: 'Enum_MPTCPOption', dlen: int,
                              bits: str, *, options: 'Option') -> 'Data_MPTCPFastclose':  # pylint: disable=unused-argument
        """Read Fast Close option.

        Structure of ``MP_FASTCLOSE`` [RFC 6824]:

        .. code-block:: text

                                1                   2                   3
            0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
           +---------------+---------------+-------+-----------------------+
           |     Kind      |    Length     |Subtype|      (reserved)       |
           +---------------+---------------+-------+-----------------------+
           |                      Option Receiver's Key                    |
           |                            (64 bits)                          |
           |                                                               |
           +---------------------------------------------------------------+

        Arguments:
            kind: option kind value
            dlen: length of remaining data
            bits: 4-bit data
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If the length is **NOT** 16.

        """
        if dlen != 13:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')

        resv = self._read_fileng(1)  # pylint: disable=unused-variable
        rkey = self._read_fileng(8)

        data = Data_MPTCPFastclose(
            kind=Enum_Option.Multipath_TCP,  # type: ignore[arg-type]
            length=dlen + 3,
            subtype=kind,
            rkey=rkey,
        )

        return data

    def _read_mode_fastopen(self, kind: 'Enum_Option', *, options: 'Option') -> 'Data_FastOpenCookie':  # pylint: disable=unused-argument
        """Read Fast Open option.

        Structure of TCP ``FASTOPEN`` [:rfc:`7413`]:

        .. code-block:: text

                                           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                                           |      Kind     |    Length     |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
           |                                                               |
           ~                            Cookie                             ~
           |                                                               |
           +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

        Arguments:
            kind: option kind value
            options: extracted TCP options

        Returns:
            Parsed option data.

        Raises:
            ProtocolError: If length is **NOT** valid.

        """
        size = self._read_unpack(1)
        if not (6 <= size <= 18) and size % 2 != 0:
            raise ProtocolError(f'{self.alias}: [OptNo {kind.value}] invalid format')
        cookie = self._read_fileng(size - 2)

        data = Data_FastOpenCookie(
            kind=kind,
            length=4,
            cookie=cookie,
        )

        return data
