# -*- coding: utf-8 -*-
"""data models for PCAP-NG file format"""

from typing import TYPE_CHECKING

from pcapkit.protocols.data.data import Data

__all__ = [
    'PCAPNG',

    'Option', 'UnknownOption',
    'EndOfOption', 'CommentOption',
    'IF_NameOption', 'IF_DescriptionOption', 'IF_IPv4AddrOption', 'IF_IPv6AddrOption',
    'IF_MACAddrOption', 'IF_EUIAddrOption', 'IF_SpeedOption', 'IF_TSResolOption',
    'IF_TZoneOption', 'IF_FilterOption', 'IF_OSOption', 'IF_FCSLenOption',
    'IF_TSOffsetOption', 'IF_HardwareOption', 'IF_TxSpeedOption', 'IF_RxSpeedOption',
    'EPB_FlagsOption', 'EPB_HashOption', 'EPB_DropCountOption', 'EPB_PacketIDOption',
    'EPB_QueueOption', 'EPB_VerdictOption',
    'NS_DNSNameOption', 'NS_DNSIP4AddrOption', 'NS_DNSIP6AddrOption',
    'ISB_StartTimeOption', 'ISB_EndTimeOption', 'ISB_IFRecvOption', 'ISB_IFDropOption',
    'ISB_FilterAcceptOption', 'ISB_OSDropOption', 'ISB_UsrDelivOption',

    'NameResolutionRecord', 'UnknownRecord', 'EndRecord', 'IPv4Record', 'IPv6Record',

    'DSBSecrets', 'UnknownSecrets', 'TLSKeyLog', 'WireGuardKeyLog', 'ZigBeeNWKKey',
    'ZigBeeAPSKey',

    'UnknownBlock', 'SectionHeaderBlock', 'InterfaceDescriptionBlock',
    'EnhancedPacketBlock', 'SimplePacketBlock', 'NameResolutionBlock',
    'InterfaceStatisticsBlock', 'SystemdJournalExportBlock', 'DecryptionSecretsBlock',
    'CustomBlock', 'PacketBlock',
]

if TYPE_CHECKING:
    from datetime import datetime
    from datetime import timezone as dt_timezone
    from decimal import Decimal
    from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
    from typing import Optional

    from typing_extensions import Literal

    from pcapkit.const.pcapng.block_type import BlockType as Enum_BlockType
    from pcapkit.const.pcapng.filter_type import FilterType as Enum_FilterType
    from pcapkit.const.pcapng.hash_algorithm import HashAlgorithm as Enum_HashAlgorithm
    from pcapkit.const.pcapng.option_type import OptionType as Enum_OptionType
    from pcapkit.const.pcapng.record_type import RecordType as Enum_RecordType
    from pcapkit.const.pcapng.secrets_type import SecretsType as Enum_SecretsType
    from pcapkit.const.pcapng.verdict_type import VerdictType as Enum_VerdictType
    from pcapkit.const.reg.linktype import LinkType as Enum_LinkType
    from pcapkit.corekit.multidict import MultiDict, OrderedMultiDict
    from pcapkit.corekit.version import VersionInfo
    from pcapkit.protocols.misc.pcapng import (PacketDirection, PacketReception, TLSKeyLabel,
                                               WireGuardKeyLabel)


class PCAPNG(Data):
    """Data model for PCAP-NG file blocks."""

    #: Block type.
    type: 'Enum_BlockType'
    #: Block total length.
    length: 'int'


class UnknownBlock(PCAPNG):
    """Data model for unknown PCAP-NG file blocks."""

    #: Block body.
    body: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', body: 'bytes') -> None: ...


class Option(Data):
    """Data model for PCAP-NG file options."""

    #: Option type.
    type: 'Enum_OptionType'
    #: Option data length.
    length: 'int'


class UnknownOption(Option):
    """Data model for unknown PCAP-NG file options."""

    #: Option data.
    data: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', data: 'bytes') -> None: ...


class EndOfOption(Option):
    """Data model for PCAP-NG file ``opt_endofopt`` options."""

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int') -> None: ...


class CommentOption(Option):
    """Data model for PCAP-NG file ``opt_comment`` options."""

    #: Comment text.
    comment: 'str'


class SectionHeaderBlock(PCAPNG):
    """Data model for PCAP-NG Section Header Block (SHB)."""

    #: Byte order.
    byteorder: 'Literal["big", "little"]'
    #: Version number.
    version: 'VersionInfo'
    #: Section length.
    section_length: 'int'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', byteorder: 'Literal["big", "little"]', version: 'VersionInfo',  # pylint: disable=unused-argument
                     section_length: 'int', options: 'OrderedMultiDict[Enum_OptionType, Option]') -> None: ...


class IF_NameOption(Option):
    """Data model for PCAP-NG file ``if_name`` options."""

    #: Interface name.
    name: 'str'


class IF_DescriptionOption(Option):
    """Data model for PCAP-NG file ``if_description`` options."""

    #: Interface description.
    description: 'str'


class IF_IPv4AddrOption(Option):
    """Data model for PCAP-NG file ``if_IPv4addr`` options."""

    #: IPv4 interface.
    interface: 'IPv4Interface'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', interface: 'IPv4Interface') -> None: ...


class IF_IPv6AddrOption(Option):
    """Data model for PCAP-NG file ``if_IPv6addr`` options."""

    #: IPv6 interface.
    interface: 'IPv6Interface'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', interface: 'IPv6Interface') -> None: ...


class IF_MACAddrOption(Option):
    """Data model for PCAP-NG file ``if_MACaddr`` options."""

    #: MAC address.
    interface: 'str'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', interface: 'str') -> None: ...


class IF_EUIAddrOption(Option):
    """Data model for PCAP-NG file ``if_EUIaddr`` options."""

    #: EUI address.
    interface: 'str'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', interface: 'str') -> None: ...


class IF_SpeedOption(Option):
    """Data model for PCAP-NG file ``if_speed`` options."""

    #: Interface speed, in bits per second.
    speed: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', speed: 'int') -> None: ...


class IF_TSResolOption(Option):
    """Data model for PCAP-NG file ``if_tsresol`` options."""

    #: Time stamp resolution, in units per second.
    resolution: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', resolution: 'int') -> None: ...


class IF_TZoneOption(Option):
    """Data model for PCAP-NG file ``if_tzone`` options."""

    #: Time zone.
    timezone: 'dt_timezone'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', timezone: 'dt_timezone') -> None: ...


class IF_FilterOption(Option):
    """Data model for PCAP-NG file ``if_filter`` options."""

    #: Filter code.
    code: 'Enum_FilterType'
    #: Filter expression.
    expression: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', code: 'Enum_FilterType', expression: 'bytes') -> None: ...


class IF_OSOption(Option):
    """Data model for PCAP-NG file ``if_os`` options."""

    #: Operating system.
    os: 'str'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', os: 'str') -> None: ...


class IF_FCSLenOption(Option):
    """Data model for PCAP-NG file ``if_fcslen`` options."""

    #: FCS length.
    fcs_length: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', fcs_length: 'int') -> None: ...


class IF_TSOffsetOption(Option):
    """Data model for PCAP-NG file ``if_tsoffset`` options."""

    #: Timestamp offset (in seconds).
    offset: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', offset: 'int') -> None: ...


class IF_HardwareOption(Option):
    """Data model for PCAP-NG file ``if_hardware`` options."""

    #: Hardware information.
    hardware: 'str'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', hardware: 'str') -> None: ...


class IF_TxSpeedOption(Option):
    """Data model for PCAP-NG file ``if_txspeed`` options."""

    #: Interface transmit speed (in bits per second).
    speed: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', speed: 'int') -> None: ...


class IF_RxSpeedOption(Option):
    """Data model for PCAP-NG file ``if_rxspeed`` options."""

    #: Interface receive speed (in bits per second).
    speed: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', speed: 'int') -> None: ...


class InterfaceDescriptionBlock(PCAPNG):
    """Data model for PCAP-NG Interface Description Block (IDB)."""

    #: Link type.
    linktype: 'Enum_LinkType'
    #: Snap length.
    snaplen: 'int'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', linktype: 'Enum_LinkType',
                     snaplen: 'int', options: 'OrderedMultiDict[Enum_OptionType, Option]') -> None: ...


class EPB_FlagsOption(Option):
    """Data model for PCAP-NG file ``epb_flags`` options."""

    #: Inbound / Outbound packet.
    direction: 'PacketDirection'
    #: Reception type.
    reception: 'PacketReception'
    #: FCS length.
    fcs_len: 'Optional[int]'
    #: Link-layer-dependent error - CRC error (bit 24).
    crc_error: 'bool'
    #: Link-layer-dependent error - packet too long error (bit 25).
    too_long: 'bool'
    #: Link-layer-dependent error - packet too short error (bit 26).
    too_short: 'bool'
    #: Link-layer-dependent error - wrong Inter Frame Gap error (bit 27).
    gap_error: 'bool'
    #: Link-layer-dependent error - unaligned frame error (bit 28).
    unaligned_error: 'bool'
    #: Link-layer-dependent error - Start Frame Delimiter error (bit 29).
    delimiter_error: 'bool'
    #: Link-layer-dependent error - preamble error (bit 30).
    preamble_error: 'bool'
    #: Link-layer-dependent error - symbol error (bit 31).
    symbol_error: 'bool'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', direction: 'PacketDirection',
                     reception: 'PacketReception', fcs_len: 'Optional[int]', crc_error: 'bool',
                     too_long: 'bool', gap_error: 'bool', unaligned_error: 'bool', delimiter_error: 'bool',
                     preamble_error: 'bool', symbole_error: 'bool') -> 'None': ...


class EPB_HashOption(Option):
    """Data model for PCAP-NG ``epb_hash`` options."""

    #: Hash algorithm.
    algorithm: 'Enum_HashAlgorithm'
    #: Hash value.
    hash: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', algorithm: 'Enum_HashAlgorithm', hash: 'bytes') -> 'None': ...


class EPB_DropCountOption(Option):
    """Data model for PCAP-NG ``epb_dropcount`` options."""

    #: Number of packets dropped by the interface.
    drop_count: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', drop_count: 'int') -> 'None': ...


class EPB_PacketIDOption(Option):
    """Data model for PCAP-NG ``epb_packetid`` options."""

    #: Packet ID.
    packet_id: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', packet_id: 'int') -> 'None': ...


class EPB_QueueOption(Option):
    """Data model for PCAP-NG ``epb_queue`` options."""

    #: Queue ID.
    queue_id: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', queue_id: 'int') -> 'None': ...


class EPB_VerdictOption(Option):
    """Data model for PCAP-NG ``epb_verdict`` options."""

    #: Verdict type.
    verdict: 'Enum_VerdictType'
    #: Verdict value.
    value: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', verdict: 'Enum_VerdictType', value: 'bytes') -> 'None': ...


class EnhancedPacketBlock(PCAPNG):
    """Data model for PCAP-NG Enhanced Packet Block (EPB)."""

    #: Interface ID.
    interface_id: 'int'
    #: Timestamp (in seconds).
    timestamp: 'datetime'
    #: Timestamp as in UNIX epoch (in seconds).
    timestamp_epoch: 'Decimal'
    #: Captured packet length.
    captured_len: 'int'
    #: Original packet length.
    original_len: 'int'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        #: Protocol chain.
        protocols: 'str'

        def __init__(self, interface_id: 'int', timestamp: 'datetime', timestamp_epoch: 'Decimal', captured_len: 'int',
                     original_len: 'int', options: 'OrderedMultiDict[Enum_OptionType, Option]') -> 'None': ...


class SimplePacketBlock(PCAPNG):
    """Data model for PCAP-NG Simple Packet Block (SPB)."""

    #: Original packet length.
    original_len: 'int'

    if TYPE_CHECKING:
        #: Protocol chain.
        protocols: 'str'

        def __init__(self, type: 'Enum_BlockType', length: 'int', original_len: 'int') -> 'None': ...


class NameResolutionRecord(Data):
    """Data model for PCAP-NG NRB records."""

    #: Record type.
    type: 'Enum_RecordType'
    #: Record value length.
    length: 'int'


class UnknownRecord(NameResolutionRecord):
    """Data model for PCAP-NG NRB unknown records."""

    #: Unknown record value.
    data: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_RecordType', length: 'int', data: 'bytes') -> 'None': ...


class EndRecord(NameResolutionRecord):
    """Data model for PCAP-NG ``nrb_record_end`` records."""

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_RecordType', length: 'int') -> 'None': ...


class IPv4Record(NameResolutionRecord):
    """Data model for PCAP-NG ``nrb_record_ipv4`` records."""

    #: IPv4 address.
    ip: 'IPv4Address'
    #: Name resolution data.
    records: 'tuple[str]'


class IPv6Record(NameResolutionRecord):
    """Data model for PCAP-NG ``nrb_record_ipv6`` records."""

    #: IPv6 address.
    ip: 'IPv6Address'
    #: Name resolution data.
    records: 'tuple[str]'


class NS_DNSNameOption(Option):
    """Data model for PCAP-NG ``ns_dnsname`` option."""

    #: DNS name.
    name: 'str'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', name: 'str') -> 'None': ...


class NS_DNSIP4AddrOption(Option):
    """Data model for PCAP-NG ``ns_dnsip4addr`` option."""

    #: IPv4 address.
    ip: 'IPv4Address'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', ip: 'IPv4Address') -> 'None': ...


class NS_DNSIP6AddrOption(Option):
    """Data model for PCAP-NG ``ns_dnsip6addr`` option."""

    #: IPv6 address.
    ip: 'IPv6Address'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', ip: 'IPv6Address') -> 'None': ...


class NameResolutionBlock(PCAPNG):
    """Data model for PCAP-NG Name Resolution Block (NRB)."""

    #: Name resolution mapping (IP address -> name).
    mapping: 'MultiDict[IPv4Address | IPv6Address, str]'
    #: Name resolution mapping (name -> IP address).
    reverse_mapping: 'MultiDict[str, IPv4Address | IPv6Address]'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', mapping: 'MultiDict[IPv4Address | IPv6Address, str]',
                     reverse_mapping: 'MultiDict[str, IPv4Address | IPv6Address]',
                     options: 'OrderedMultiDict[Enum_OptionType, Option]') -> 'None': ...


class ISB_StartTimeOption(Option):
    """Data model for PCAP-NG ``isb_starttime`` option."""

    #: Start time.
    timestamp: 'datetime'
    #: Start time as in UNIX epoch (in seconds).
    timestamp_epoch: 'Decimal'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', timestamp: 'datetime',
                     timestamp_epoch: 'Decimal') -> 'None': ...


class ISB_EndTimeOption(Option):
    """Data model for PCAP-NG ``isb_endtime`` option."""

    #: End time.
    timestamp: 'datetime'
    #: End time as in UNIX epoch (in seconds).
    timestamp_epoch: 'Decimal'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', timestamp: 'datetime',
                     timestamp_epoch: 'Decimal') -> 'None': ...


class ISB_IFRecvOption(Option):
    """Data model for PCAP-NG ``isb_ifrecv`` option."""

    #: Number of packets received.
    packets: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', packets: 'int') -> 'None': ...


class ISB_IFDropOption(Option):
    """Data model for PCAP-NG ``isb_ifdrop`` option."""

    #: Number of packets dropped.
    packets: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', packets: 'int') -> 'None': ...


class ISB_FilterAcceptOption(Option):
    """Data model for PCAP-NG ``isb_filteraccept`` option."""

    #: Number of packets accepted by the filter.
    packets: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', packets: 'int') -> 'None': ...


class ISB_OSDropOption(Option):
    """Data model for PCAP-NG ``isb_osdrop`` option."""

    #: Number of packets dropped by the operating system.
    packets: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', packets: 'int') -> 'None': ...


class ISB_UsrDelivOption(Option):
    """Data model for PCAP-NG ``isb_usrdeliv`` option."""

    #: Number of packets delivered to the user.
    packets: 'int'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_OptionType', length: 'int', packets: 'int') -> 'None': ...


class InterfaceStatisticsBlock(PCAPNG):
    """Data model for PCAP-NG Interface Statistics Block (ISB)."""

    #: Interface ID.
    interface_id: 'int'
    #: Timestamp.
    timestamp: 'datetime'
    #: Timestamp as in UNIX epoch (in seconds).
    timestamp_epoch: 'Decimal'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', interface_id: 'int', timestamp: 'datetime',
                     timestamp_epoch: 'Decimal', options: 'OrderedMultiDict[Enum_OptionType, Option]') -> 'None': ...


class SystemdJournalExportBlock(PCAPNG):
    """Data model for PCAP-NG :manpage:`systemd(1)` Journal Export Block."""

    #: Journal entry.
    data: 'tuple[OrderedMultiDict[str, str | bytes]]'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', data: 'tuple[OrderedMultiDict[str, str | bytes]]') -> 'None': ...


class DSBSecrets(Data):
    """Data model for DSB secrets data."""


class UnknownSecrets(DSBSecrets):
    """Data model for unknown DSB secrets."""

    #: Secrets data.
    data: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, data: 'bytes') -> 'None': ...


class TLSKeyLog(DSBSecrets):
    """Data model for TLS key log DSB secrets."""

    #: TLS key log entries.
    entries: 'OrderedMultiDict[TLSKeyLabel, bytes]'

    if TYPE_CHECKING:
        def __init__(self, entries: 'OrderedMultiDict[TLSKeyLabel, bytes]') -> 'None': ...


class WireGuardKeyLog(DSBSecrets):
    """Data model for WireGuard key DSB secrets."""

    #: WireGuard Key Log entries.
    entries: 'OrderedMultiDict[WireGuardKeyLabel, bytes]'

    if TYPE_CHECKING:
        def __init__(self, entries: 'OrderedMultiDict[WireGuardKeyLabel, bytes]') -> 'None': ...


class ZigBeeNWKKey(DSBSecrets):
    """Data model for ZigBEE NWK Key and ZigBee PANID secrets data."""

    #: AES-128 NKW key.
    nwk_key: 'bytes'
    #: PAN ID.
    pan_id: 'int'

    if TYPE_CHECKING:
        def __init__(self, nwk_key: 'bytes', pan_id: 'int') -> 'None': ...


class ZigBeeAPSKey(DSBSecrets):
    """Data model for ZigBEE APS Key secrets data."""

    #: AES-128 APS key.
    aps_key: 'bytes'
    #: PAN ID.
    pan_id: 'int'
    #: Node short address.
    short_address: 'int'

    if TYPE_CHECKING:
        def __init__(self, aps_key: 'bytes', pan_id: 'int', short_address: 'int') -> 'None': ...


class DecryptionSecretsBlock(PCAPNG):
    """Data model for PCAP-NG Decryption Secrets Block (DSB)."""

    #: Secrets type.
    secrets_type: 'Enum_SecretsType'
    #: Secrets length.
    secrets_length: 'int'
    #: Secrets data.
    secrets_data: 'DSBSecrets'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', secrets_type: 'Enum_SecretsType',
                     secrets_length: 'int', secrets_data: 'DSBSecrets',
                     options: 'OrderedMultiDict[Enum_OptionType, Option]') -> 'None': ...


class CustomBlock(PCAPNG):
    """Data model for PCAP-NG Custom Block (CB)."""

    #: Private enterprise number.
    pen: 'int'
    #: Custom block data.
    data: 'bytes'

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_BlockType', length: 'int', pen: 'int', data: 'bytes') -> 'None': ...


class PacketBlock(PCAPNG):
    """Data model for PCAP-NG Packet Block (obsolete)."""

    #: Interface ID.
    interface_id: 'int'
    #: Drops count.
    drop_count: 'int'
    #: Timestamp.
    timestamp: 'datetime'
    #: Timestamp as in UNIX epoch (in seconds).
    timestamp_epoch: 'Decimal'
    #: Captured packet length.
    captured_length: 'int'
    #: Original packet length.
    original_length: 'int'
    #: Options.
    options: 'OrderedMultiDict[Enum_OptionType, Option]'

    if TYPE_CHECKING:
        #: Protocol chain.
        protocols: 'str'

        def __init__(self, type: 'Enum_BlockType', length: 'int', interface_id: 'int', drop_count: 'int',
                     timestamp: 'datetime', timestamp_epoch: 'Decimal', captured_length: 'int',
                     original_length: 'int', protocols: 'str',
                     options: 'OrderedMultiDict[Enum_OptionType, Option]') -> 'None': ...
