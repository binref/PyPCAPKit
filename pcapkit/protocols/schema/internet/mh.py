# -*- coding: utf-8 -*-
# mypy: disable-error-code=assignment
"""header schema for mobility header"""

import collections
import datetime
import math
from typing import TYPE_CHECKING

from pcapkit.const.mh.access_type import AccessType as Enum_AccessType
from pcapkit.const.mh.ack_status_code import ACKStatusCode as Enum_ACKStatusCode
from pcapkit.const.mh.ani_suboption import ANISuboption as Enum_ANISuboption
from pcapkit.const.mh.auth_subtype import AuthSubtype as Enum_AuthSubtype
from pcapkit.const.mh.binding_ack_flag import BindingACKFlag as Enum_BindingACKFlag
from pcapkit.const.mh.binding_revocation import BindingRevocation as Enum_BindingRevocation
from pcapkit.const.mh.binding_update_flag import BindingUpdateFlag as Enum_BindingUpdateFlag
from pcapkit.const.mh.cga_extension import CGAExtension as Enum_CGAExtension
from pcapkit.const.mh.cga_type import CGAType as Enum_CGAType
from pcapkit.const.mh.dhcp_support_mode import DHCPSupportMode as Enum_DHCPSupportMode
from pcapkit.const.mh.dns_status_code import DNSStatusCode as Enum_DNSStatusCode
from pcapkit.const.mh.dsmip6_tls_packet import DSMIP6TLSPacket as Enum_DSMIP6TLSPacket
from pcapkit.const.mh.dsmipv6_home_address import DSMIPv6HomeAddress as Enum_DSMIPv6HomeAddress
from pcapkit.const.mh.enumerating_algorithm import EnumeratingAlgorithm as Enum_EnumeratingAlgorithm
from pcapkit.const.mh.fb_ack_status import FlowBindingACKStatus as Enum_FlowBindingACKStatus
from pcapkit.const.mh.fb_action import FlowBindingAction as Enum_FlowBindingAction
from pcapkit.const.mh.fb_indication_trigger import \
    FlowBindingIndicationTrigger as Enum_FlowBindingIndicationTrigger
from pcapkit.const.mh.fb_type import FlowBindingType as Enum_FlowBindingType
from pcapkit.const.mh.flow_id_status import FlowIDStatus as Enum_FlowIDStatus
from pcapkit.const.mh.flow_id_suboption import FlowIDSuboption as Enum_FlowIDSuboption
from pcapkit.const.mh.handoff_type import HandoffType as Enum_HandoffType
from pcapkit.const.mh.handover_ack_flag import HandoverACKFlag as Enum_HandoverACKFlag
from pcapkit.const.mh.handover_ack_status import HandoverACKStatus as Enum_HandoverACKStatus
from pcapkit.const.mh.handover_initiate_flag import \
    HandoverInitiateFlag as Enum_HandoverInitiateFlag
from pcapkit.const.mh.home_address_reply import HomeAddressReply as Enum_HomeAddressReply
from pcapkit.const.mh.lla_code import LLACode as Enum_LLACode
from pcapkit.const.mh.lma_mag_suboption import \
    LMAControlledMAGSuboption as Enum_LMAControlledMAGSuboption
from pcapkit.const.mh.mn_group_id import MNGroupID as Enum_MNGroupID
from pcapkit.const.mh.mn_id_subtype import MNIDSubtype as Enum_MNIDSubtype
from pcapkit.const.mh.operator_id import OperatorID as Enum_OperatorID
from pcapkit.const.mh.option import Option as Enum_Option
from pcapkit.const.mh.packet import Packet as Enum_Packet
from pcapkit.const.mh.qos_attribute import QoSAttribute as Enum_QoSAttribute
from pcapkit.const.mh.revocation_status_code import \
    RevocationStatusCode as Enum_RevocationStatusCode
from pcapkit.const.mh.revocation_trigger import RevocationTrigger as Enum_RevocationTrigger
from pcapkit.const.mh.status_code import StatusCode as Enum_StatusCode
from pcapkit.const.mh.traffic_selector import TrafficSelector as Enum_TrafficSelector
from pcapkit.const.mh.upa_status import \
    UpdateNotificationACKStatus as Enum_UpdateNotificationACKStatus
from pcapkit.const.mh.upn_reason import UpdateNotificationReason as Enum_UpdateNotificationReason
from pcapkit.const.reg.transtype import TransType as Enum_TransType
from pcapkit.corekit.fields.collections import ListField, OptionField
from pcapkit.corekit.fields.ipaddress import IPv6AddressField
from pcapkit.corekit.fields.misc import (ConditionalField, ForwardMatchField, PayloadField,
                                         SchemaField, SwitchField)
from pcapkit.corekit.fields.numbers import (EnumField, UInt8Field, UInt16Field, UInt32Field,
                                            UInt64Field)
from pcapkit.corekit.fields.strings import BitField, BytesField, PaddingField, StringField
from pcapkit.protocols.schema.schema import Schema, schema_final
from pcapkit.utilities.logging import SPHINX_TYPE_CHECKING

__all__ = [
    'MH',

    'Packet',
    'UnknownMessage',

    'Option',
    'UnassignedOption', 'PadOption', 'BindRefreshAdviceOption', 'AlternateCareofAddressOption',
    'NonceIndicesOption', 'BindingAuthorizationDataOption', 'MobileNetworkPrefixOption',
    'LinkLayerAddressOption', 'MNIDOption', 'AuthOption', 'MesgIDOption', 'CGAParametersRequestOption',
    'CGAParametersOption', 'SignatureOption', 'PermanentHomeKeygenTokenOption', 'CareofTestInitOption',
    'CareofTestOption',

    'CGAParameter',

    'CGAExtension',
    'UnknownExtension', 'MultiPrefixExtension',

]

if TYPE_CHECKING:
    from datetime import datetime as dt_type
    from ipaddress import IPv6Address
    from typing import Any

    from pcapkit.corekit.fields.field import _Field as Field
    from pcapkit.protocols.protocol import Protocol

if SPHINX_TYPE_CHECKING:
    from typing_extensions import TypedDict

    class ANSIKeyLengthTest(TypedDict):
        """Length test for ANSI.1 encoded data, c.f.,
        :attr:`CGAParameter.public_key_test`."""

        len: int

    class MultiPrefixExtensionFlags(TypedDict):
        """Flags for :attr:`MultiPrefixExtension.flags`."""

        P: int


def mh_data_selector(pkt: 'dict[str, Any]') -> 'Field':
    """Selector function for :attr:`MH.data` field.

    Args:
        pkt: Packet data.

    Returns:
        Returns a :class:`~pcapkit.corekit.fields.misc.SchemaField`
        wrapped :class:`~pcapkit.protocols.schema.misc.mh.Packet`
        subclass instance.

    """
    type = pkt['type']  # type: Enum_Packet
    length = pkt['length'] * 8 + 2

    return SchemaField(length=length, schema=UnknownMessage)


def mn_id_selector(pkt: 'dict[str, Any]') -> 'Field':
    """Selector function for :attr:`MNIDOption.identifier` field.

    Args:
        pkt: Packet data.

    Returns:
        Returns a :class:`~pcapkit.corekit.fields.field.Field` instance
        corresponding to the subtype.

    """
    subtype = pkt['subtype']  # type: Enum_MNIDSubtype
    if subtype == Enum_MNIDSubtype.NAI:
        return StringField(length=pkt['length'] - 1)
    if subtype == Enum_MNIDSubtype.IPv6_Address:
        return IPv6AddressField()
    return BytesField(length=pkt['length'] - 1)


class Option(Schema):
    """Header schema for MH options."""

    #: Option type.
    type: 'Enum_Option' = EnumField(length=1, namespace=Enum_Option)
    #: Option length (excl. type and length fields), conditional in case of
    #: ``Pad1`` option.
    length: 'int' = ConditionalField(
        UInt8Field(default=0),
        lambda pkt: pkt['type'] != Enum_Option.Pad1,
    )

    def post_process(self, packet: 'dict[str, Any]') -> 'Option':
        """Revise ``schema`` data after unpacking process.

        Args:
            packet: Unpacked data.

        Returns:
            Revised schema.

        """
        # for Pad1 option, length is always 1
        if self.type == Enum_Option.pad1:
            self.length = 0
        return self


@schema_final
class UnassignedOption(Option):
    """Header schema for unassigned MH options."""

    #: Option data.
    data: 'bytes' = BytesField(length=lambda pkt: pkt['length'])

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', data: 'bytes') -> 'None': ...


@schema_final
class PadOption(Option):
    """Header schema for MH padding options."""

    #: Option data.
    data: 'bytes' = PaddingField(length=lambda pkt: pkt.get('length', 0))

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int') -> 'None': ...


@schema_final
class BindRefreshAdviceOption(Option):
    """Header schema for MH binding refresh advice options."""

    #: Refresh interval.
    interval: 'int' = UInt16Field()

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', interval: 'int') -> 'None': ...


@schema_final
class AlternateCareofAddressOption(Option):
    """Header schema for MH alternate care-of address options."""

    #: Alternate care-of address.
    address: 'IPv6Address' = IPv6AddressField()

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', address: 'IPv6Address | str | bytes | int') -> 'None': ...


@schema_final
class NonceIndicesOption(Option):
    """Header schema for MH nonce indices options."""

    #: Home nonce index.
    home: 'int' = UInt16Field()
    #: Care-of nonce index.
    careof: 'int' = UInt16Field()

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', home: 'int', careof: 'int') -> 'None': ...


@schema_final
class BindingAuthorizationDataOption(Option):
    """Header schema for MH binding authorization data options."""

    #: Authenticator.
    data: 'bytes' = BytesField(length=lambda pkt: pkt['length'])

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', data: 'bytes') -> 'None': ...


@schema_final
class MobileNetworkPrefixOption(Option):
    """Header schema for MH mobile network prefix options."""

    #: Reserved.
    reserved: 'bytes' = PaddingField(length=1)
    #: Prefix length.
    prefix_length: 'int' = UInt8Field()
    #: Mobile network prefix.
    prefix: 'IPv6Address' = IPv6AddressField()

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', prefix_length: 'int', prefix: 'IPv6Address | int | bytes | str') -> 'None': ...


@schema_final
class LinkLayerAddressOption(Option):
    """Header schema for MH link-layer address (MH-LLA) options."""

    #: Option code.
    code: 'Enum_LLACode' = EnumField(length=1, namespace=Enum_LLACode)
    #: Link-layer address (LAA).
    lla: 'bytes' = BytesField(length=lambda pkt: pkt['length'] - 1)

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', code: 'Enum_LLACode', lla: 'bytes') -> 'None': ...


@schema_final
class MNIDOption(Option):
    """Header schema for MH mobile node identifier (MNID) options."""

    #: Subtype.
    subtype: 'Enum_MNIDSubtype' = EnumField(length=1, namespace=Enum_MNIDSubtype)
    #: Identifier.
    identifier: 'bytes | str | IPv6Address' = SwitchField(selector=mn_id_selector)

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', subtype: 'Enum_MNIDSubtype', identifier: 'bytes | str | IPv6Address | int') -> 'None': ...


@schema_final
class AuthOption(Option):
    """Header schema for Mobility Message Authentication options."""

    #: Subtype.
    subtype: 'Enum_AuthSubtype' = EnumField(length=1, namespace=Enum_AuthSubtype)
    #: Mobility SPI.
    spi: 'int' = UInt32Field()
    #: Authentication data.
    data: 'bytes' = BytesField(length=lambda pkt: pkt['length'] - 5)

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', subtype: 'Enum_AuthSubtype', spi: 'int', data: 'bytes') -> 'None': ...


@schema_final
class MesgIDOption(Option):
    """Header schema for Mobility Message Replay Protection options."""

    #: Timestamp (seconds since January 1st, 1970, c.f., :rfc:`1305`).
    seconds: 'int' = UInt32Field()
    #: Timestamp fractions (1/2**32 seconds per unit, c.f., :rfc:`1305`).
    fraction: 'int' = UInt32Field()

    def post_process(self, packet: 'dict[str, Any]') -> 'MesgIDOption':
        """Revise ``schema`` data after unpacking process.

        Args:
            packet: Unpacked data.

        Returns:
            Revised schema.

        """
        self = super().post_process(packet)

        # convert timestamp to datetime
        # c.f., http://tickelton.gitlab.io/articles/ntp-timestamps/
        ts_sec = self.seconds - 2_208_988_800  # 70 years
        ts_usec = math.floor(self.fraction / 2**32)

        self.timestamp = datetime.datetime.fromtimestamp(ts_sec + ts_usec, tz=datetime.timezone.utc)

        return self

    if TYPE_CHECKING:
        #: Timestamp interval (since UNIX-epoch).
        timestamp: 'dt_type'

        def __init__(self, type: 'Enum_Option', length: 'int', seconds: 'int', fraction: 'int') -> 'None': ...


@schema_final
class CGAParametersRequestOption(Option):
    """Header schema for CGA Parameters Request options."""

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int') -> 'None': ...


class CGAExtension(Schema):
    """Header schema for CGA extensions."""

    #: Extension type.
    type: 'Enum_CGAExtension' = EnumField(length=2, namespace=Enum_CGAExtension)
    #: Extension data length.
    length: 'int' = UInt16Field()


@schema_final
class UnknownExtension(CGAExtension):
    """Header schema for unknown CGA extensions."""

    #: Extension data.
    data: 'bytes' = BytesField(length=lambda pkt: pkt['length'])

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_CGAExtension', length: 'int', data: 'bytes') -> 'None': ...


@schema_final
class MultiPrefixExtension(CGAExtension):
    """Header schema for Multi-Prefix CGA extensions."""

    #: Flags.
    flags: 'MultiPrefixExtensionFlags' = BitField(length=4, namespace={
        'P': (0, 1),
    })
    #: Prefixes.
    prefixes: 'list[int]' = ListField(
        length=lambda pkt: pkt['length'] - 4,
        item_type=UInt64Field(),
    )

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_CGAExtension', length: 'int', flags: 'MultiPrefixExtensionFlags', prefixes: 'list[int]') -> 'None': ...


@schema_final
class CGAParameter(Schema):
    """Header schema for CGA Parameters."""

    #: Modifier.
    modifier: 'Enum_CGAType' = EnumField(length=16, namespace=Enum_CGAType)
    #: Subnet prefix.
    prefix: 'int' = UInt64Field()
    #: Collision count.
    collision_count: 'int' = UInt8Field()
    #: Public key length test.
    public_key_test: 'ANSIKeyLengthTest' = ForwardMatchField(BitField(length=2, namespace={
        'len': (8, 8),
    }))
    #: Public key (ASN.1 encoded).
    public_key: 'bytes' = BytesField(length=lambda pkt: pkt['public_key_test']['len'] + 2)  # 2 bytes for type & length
    #: Extension fields.
    extensions: 'list[CGAExtension]' = OptionField(
        length=lambda pkt: pkt['length'] - 25 - len(pkt['public_key']),
        base_schema=CGAExtension,
        type_name='type',
        registry=collections.defaultdict(lambda: UnknownExtension, {
            Enum_CGAExtension.Multi_Prefix: MultiPrefixExtension,
        }),
        eool=None,
    )

    if TYPE_CHECKING:
        def __init__(self, modifier: 'Enum_CGAType', prefix: 'int', collision_count: 'int', public_key: 'bytes',
                     extensions: 'list[CGAExtension | bytes]') -> 'None': ...


@schema_final
class CGAParametersOption(Option):
    """Header schema for CGA Parameters options."""

    #: CGA parameters, c.f., :rfc:`3972`.
    parameters: 'list[CGAParameter]' = ListField(
        length=lambda pkt: pkt['length'],
        item_type=SchemaField(schema=CGAParameter),
    )

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', parameters: 'list[CGAParameter | bytes]') -> 'None': ...


@schema_final
class SignatureOption(Option):
    """Header schema for MH Signature options."""

    #: Signature.
    signature: 'bytes' = BytesField(length=lambda pkt: pkt['length'])

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', signature: 'bytes') -> 'None': ...


@schema_final
class PermanentHomeKeygenTokenOption(Option):
    """Header schema for Permanent Home Keygen Token options."""

    #: Permanent home keygen token.
    token: 'bytes' = BytesField(length=lambda pkt: pkt['length'])

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', token: 'bytes') -> 'None': ...


@schema_final
class CareofTestInitOption(Option):
    """Header schema for MH Care-of Test Init options."""

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int') -> 'None': ...


@schema_final
class CareofTestOption(Option):
    """Header schema for MH Care-of Test options."""

    #: Care-of keygen token.
    token: 'bytes' = BytesField(length=8)

    if TYPE_CHECKING:
        def __init__(self, type: 'Enum_Option', length: 'int', token: 'bytes') -> 'None': ...


class Packet(Schema):
    """Header schema for MH packet data."""


@schema_final
class UnknownMessage(Packet):
    """Header schema for MH unknown message type."""

    #: Message data.
    data: 'bytes' = BytesField(length=lambda pkt: pkt['__length__'])

    if TYPE_CHECKING:
        def __init__(self, data: 'bytes') -> 'None': ...


@schema_final
class MH(Schema):
    """Header schema for MH packets."""

    #: Next header.
    next: 'Enum_TransType' = EnumField(length=1, namespace=Enum_TransType)
    #: Header length.
    length: 'int' = UInt8Field()
    #: MH type.
    type: 'Enum_Packet' = EnumField(length=1, namespace=Enum_Packet)
    #: Reserved.
    reserved: 'bytes' = PaddingField(length=1)
    #: Checksum.
    chksum: 'bytes' = BytesField(length=2)
    #: Message data.
    data: 'Packet' = SwitchField(selector=mh_data_selector)
    #: Payload.
    payload: 'bytes' = PayloadField()

    if TYPE_CHECKING:
        def __init__(self, next: 'Enum_TransType', length: 'int', type: 'Enum_Packet',
                     chksum: 'bytes', data: 'Packet | bytes', payload: 'bytes | Protocol | Schema') -> 'None': ...
