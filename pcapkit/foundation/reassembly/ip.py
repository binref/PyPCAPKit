# -*- coding: utf-8 -*-
"""IP Datagram Reassembly
============================

:mod:`pcapkit.foundation.reassembly.ip` contains
:class:`~pcapkit.foundation.reassembly.ip.IP_Reassembly`
only, which reconstructs fragmented IP packets back to
origin. The following algorithm implement is based on IP
reassembly procedure introduced in :rfc:`791`, using
``RCVBT`` (fragment receivedbit table). Though another
algorithm is explained in :rfc:`815`, replacing ``RCVBT``,
however, this implement still used the elder one.

"""
from typing import TYPE_CHECKING, Generic

from pcapkit.foundation.reassembly.data.ip import AT, Buffer, BufferID, Datagram, DatagramID, Packet
from pcapkit.foundation.reassembly.reassembly import Reassembly

if TYPE_CHECKING:
    from pcapkit.const.reg.transtype import TransType

__all__ = ['IP_Reassembly']


class IP_Reassembly(Reassembly[Packet[AT], Datagram[AT], BufferID, Buffer[AT]], Generic[AT]):  # pylint: disable=abstract-method
    """Reassembly for IP payload.

    Important:
        This class is not intended to be instantiated directly,
        but rather used as a base class for the protocol-aware
        reassembly classes.

    """

    ##########################################################################
    # Methods.
    ##########################################################################

    def reassembly(self, info: 'Packet[AT]') -> 'None':
        """Reassembly procedure.

        Arguments:
            info: info dict of packets to be reassembled

        """
        # clear cache
        self._newflg = False
        self.__cached__.clear()

        BUFID = info.bufid  # Buffer Identifier
        FO = info.fo        # Fragment Offset
        IHL = info.ihl      # Internet Header Length
        MF = info.mf        # More Fragments flag
        TL = info.tl        # Total Length

        # when non-fragmented (possibly discarded) packet received
        if not FO and not MF:
            if BUFID in self._buffer:
                self._dtgram.extend(
                    self.submit(self._buffer.pop(BUFID), bufid=BUFID)
                )
                return

        # initialise buffer with BUFID
        if BUFID not in self._buffer:
            self._buffer[BUFID] = Buffer(
                TDL=-1,                              # Total Data Length
                RCVBT=bytearray(8191),              # Fragment Received Bit Table
                index=[],                           # index record
                header=b'' if FO else info.header,  # header buffer
                datagram=bytearray(65535),          # data buffer
            )
        else:
            # put header into header buffer
            if not FO:  # pylint: disable=else-if-used
                self._buffer[BUFID].__update__(header=info.header)

        # append packet index
        self._buffer[BUFID].index.append(info.num)

        # put data into data buffer
        start = FO
        stop = TL - IHL + FO
        self._buffer[BUFID].datagram[start:stop] = info.payload

        # set RCVBT bits (in 8 octets)
        start = FO // 8
        stop = FO // 8 + (TL - IHL + 7) // 8
        self._buffer[BUFID].RCVBT[start:stop] = b'\x01' * (stop - start + 1)

        # get total data length (header excludes)
        TDL = 0
        if not MF:
            TDL = TL - IHL + FO
            self._buffer[BUFID].__update__(TDL=TDL)

        # when datagram is reassembled in whole
        start = 0
        stop = (TDL + 7) // 8
        if TDL and all(self._buffer[BUFID].RCVBT[start:stop]):
            self._dtgram.extend(
                self.submit(self._buffer.pop(BUFID), bufid=BUFID, checked=True)
            )

    def submit(self, buf: 'Buffer[AT]', *, bufid: 'tuple[AT, AT, int, TransType]',  # type: ignore[override] # pylint: disable=arguments-differ
               checked: 'bool' = False) -> 'list[Datagram[AT]]':
        """Submit reassembled payload.

        Arguments:
            buf: buffer dict of reassembled packets
            bufid: buffer identifier
            checked: buffer consistency checked flag

        Returns:
            Reassembled packets.

        """
        TDL = buf.TDL
        RCVBT = buf.RCVBT
        index = buf.index
        header = buf.header
        datagram = buf.datagram

        start = 0
        stop = (TDL + 7) // 8
        flag = checked or (TDL and all(RCVBT[start:stop]))
        # if datagram is not implemented
        if not flag and self._strflg:
            data = []  # type: list[bytes]
            byte = bytearray()
            # extract received payload
            for (bctr, bit) in enumerate(RCVBT):
                if bit:     # received bit
                    this = bctr * 8
                    that = this + 8
                    byte += datagram[this:that]
                else:       # missing bit
                    if byte:    # strip empty payload
                        data.append(bytes(byte))
                    byte = bytearray()
            # strip empty packets
            if data or header:
                packet = Datagram(
                    completed=False,
                    id=DatagramID(
                        src=bufid[0],
                        dst=bufid[1],
                        id=bufid[2],
                        proto=bufid[3],
                    ),
                    index=tuple(index),
                    header=header,
                    payload=tuple(data),
                    packet=None,
                )
        # if datagram is reassembled in whole
        else:
            payload = datagram[:TDL]
            packet = Datagram(
                completed=True,
                id=DatagramID(
                    src=bufid[0],
                    dst=bufid[1],
                    id=bufid[2],
                    proto=bufid[3],
                ),
                index=tuple(index),
                header=header,
                payload=bytes(payload),
                packet=self.protocol.analyze(bufid[3], bytes(payload)),
            )
        return [packet]
