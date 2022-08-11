#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#	tcprelay.py - TCP connection relay for usbmuxd
#
# Original work Copyright (C) 2009  Hector Martin "marcan" <hector@marcansoft.com>
# Modified work Copyright (C) 2019  phx <https://github.com/phx>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 or version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
import os
import socket
import struct
import plistlib
import socketserver
from select import select

from permasigner.ps_logger import Logger, Colors


class MuxError(Exception):
    pass


class MuxVersionError(MuxError):
    pass


class SafeStreamSocket:
    def __init__(self, address, family):
        self.sock = socket.socket(family, socket.SOCK_STREAM)
        self.sock.connect(address)

    def send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(bytes(msg)[totalsent:])
            if sent == 0:
                raise MuxError("socket connection broken")
            totalsent = totalsent + sent

    def recv(self, size):
        msg = b''
        while len(msg) < size:
            chunk = self.sock.recv(size - len(msg))
            if chunk == b'':
                raise MuxError("socket connection broken")
            msg = msg + chunk
        return msg


class MuxDevice(object):
    def __init__(self, devid, usbprod, serial, location):
        self.devid = devid
        self.usbprod = usbprod
        self.serial = serial
        self.location = location

    def __str__(self):
        return f"<MuxDevice: ID {self.devid} ProdID {format(self.usbprod, '#04x')} Serial '{self.serial}' " \
               f"Location {format(self.location, '#x')}"


class BinaryProtocol(object):
    TYPE_RESULT = 1
    TYPE_CONNECT = 2
    TYPE_LISTEN = 3
    TYPE_DEVICE_ADD = 4
    TYPE_DEVICE_REMOVE = 5
    VERSION = 0

    def __init__(self, socket):
        self.socket = socket
        self.connected = False

    def _pack(self, req, payload):
        if req == self.TYPE_CONNECT:
            return struct.pack("IH", payload['DeviceID'], payload['PortNumber']) + b"\x00\x00"
        elif req == self.TYPE_LISTEN:
            return ""
        else:
            raise ValueError(f"Invalid outgoing request type {req}")

    def _unpack(self, resp, payload):
        if resp == self.TYPE_RESULT:
            return {'Number': struct.unpack("I", payload)[0]}
        elif resp == self.TYPE_DEVICE_ADD:
            devid, usbpid, serial, pad, location = struct.unpack(
                "IH256sHI", payload)
            serial = serial.decode().split("\0")[0]
            return {'DeviceID': devid,
                    'Properties': {'LocationID': location, 'SerialNumber': serial, 'ProductID': usbpid}}
        elif resp == self.TYPE_DEVICE_REMOVE:
            devid = struct.unpack("I", payload)[0]
            return {'DeviceID': devid}
        else:
            raise MuxError(f"Invalid incoming request type {resp}")

    def sendpacket(self, req, tag, payload=None):
        if payload is None:
            payload = {}
        payload = self._pack(req, payload)
        if not isinstance(payload, bytes):
            payload = bytes(payload, 'utf-8')
        if self.connected:
            raise MuxError("Mux is connected, cannot issue control packets")
        length = 16 + len(payload)
        data = struct.pack('4I', length, self.VERSION, req, tag) + payload
        self.socket.send(data)

    def getpacket(self):
        if self.connected:
            raise MuxError("Mux is connected, cannot issue control packets")
        dlen = self.socket.recv(4)
        dlen = struct.unpack("I", dlen)[0]
        body = self.socket.recv(dlen - 4)
        version, resp, tag = struct.unpack("3I", body[:0xc])
        if version != self.VERSION:
            raise MuxVersionError(
                f"Version mismatch: expected {self.VERSION}, got {version}")
        payload = self._unpack(resp, body[0xc:])
        return resp, tag, payload


class PlistProtocol(BinaryProtocol):
    TYPE_RESULT = "Result"
    TYPE_CONNECT = "Connect"
    TYPE_LISTEN = "Listen"
    TYPE_DEVICE_ADD = "Attached"
    TYPE_DEVICE_REMOVE = "Detached"
    TYPE_PLIST = 8
    VERSION = 1

    def __init__(self, socket):
        BinaryProtocol.__init__(self, socket)

    def _pack(self, req, payload):
        return payload

    def _unpack(self, resp, payload):
        return payload

    def sendpacket(self, req, tag, payload=None):
        if payload is None:
            payload = {}
        payload['ClientVersionString'] = 'usbmux.py by marcan - python2/3 compatibility by phx'
        if isinstance(req, int):
            req = [self.TYPE_CONNECT, self.TYPE_LISTEN][req - 2]
        payload['MessageType'] = req
        payload['ProgName'] = 'tcprelay'
        BinaryProtocol.sendpacket(
            self, self.TYPE_PLIST, tag, plistlib.dumps(payload))

    def getpacket(self):
        resp, tag, payload = BinaryProtocol.getpacket(self)
        if resp != self.TYPE_PLIST:
            raise MuxError(f"Received non-plist type {resp}")
        payload = plistlib.loads(payload)
        return payload['MessageType'], tag, payload


class MuxConnection(object):
    def __init__(self, socketpath, protoclass):
        self.socketpath = socketpath
        if os.environ.get("HOST_IS_WINDOWS", False):
            family = socket.AF_INET
            address = ('host.docker.internal', 27015)
        else:
            family = socket.AF_UNIX
            address = self.socketpath
        self.socket = SafeStreamSocket(address, family)
        self.proto = protoclass(self.socket)
        self.pkttag = 1
        self.devices = []

    def _getreply(self):
        while True:
            resp, tag, data = self.proto.getpacket()
            if resp == self.proto.TYPE_RESULT:
                return tag, data
            else:
                raise MuxError(f"Invalid packet type received: {resp}")

    def _processpacket(self):
        resp, tag, data = self.proto.getpacket()
        if resp == self.proto.TYPE_DEVICE_ADD:
            self.devices.append(
                MuxDevice(data['DeviceID'], data['Properties']['ProductID'], data['Properties']['SerialNumber'],
                          data['Properties']['LocationID']))
        elif resp == self.proto.TYPE_DEVICE_REMOVE:
            for dev in self.devices:
                if dev.devid == data['DeviceID']:
                    self.devices.remove(dev)
        elif resp == self.proto.TYPE_RESULT:
            raise MuxError(f"Unexpected result: {resp}")
        else:
            raise MuxError(f"Invalid packet type received: {resp}")

    def _exchange(self, req, payload=None):
        if payload is None:
            payload = {}
        mytag = self.pkttag
        self.pkttag += 1
        self.proto.sendpacket(req, mytag, payload)
        recvtag, data = self._getreply()
        if recvtag != mytag:
            raise MuxError('Replay tag mismatch: expected',
                           str(mytag), 'received', str(recvtag))
        return data['Number']

    def listen(self):
        ret = self._exchange(self.proto.TYPE_LISTEN)
        if ret != 0:
            raise MuxError(f"Listen failed: error {ret}")

    def process(self, timeout=None):
        if self.proto.connected:
            raise MuxError(
                "Socket is connected, cannot process listener events")
        rlo, wlo, xlo = select([self.socket.sock], [], [
            self.socket.sock], timeout)
        if xlo:
            self.socket.sock.close()
            raise MuxError("Exception in listener socket")
        if rlo:
            self._processpacket()

    def connect(self, device, port):
        ret = self._exchange(self.proto.TYPE_CONNECT,
                             {'DeviceID': device.devid, 'PortNumber': ((port << 8) & 0xFF00) | (port >> 8)})
        if ret != 0:
            raise MuxError(f"Connect failed: error {ret}")
        self.proto.connected = True
        return self.socket.sock

    def close(self):
        self.socket.sock.close()


class USBMux(object):
    def __init__(self, socketpath):
        self.socketpath = socketpath
        self.listener = MuxConnection(self.socketpath, BinaryProtocol)
        try:
            self.listener.listen()
            self.version = 0
            self.protoclass = BinaryProtocol
        except MuxVersionError:
            self.listener = MuxConnection(self.socketpath, PlistProtocol)
            self.listener.listen()
            self.protoclass = PlistProtocol
            self.version = 1
        self.devices = self.listener.devices

    def process(self, timeout=None):
        self.listener.process(timeout)

    def connect(self, device, port):
        connector = MuxConnection(self.socketpath, self.protoclass)
        return connector.connect(device, port)


class SocketRelay(object):
    def __init__(self, a, b, maxbuf=65535):
        self.a = a
        self.b = b
        self.atob = b''
        self.btoa = b''
        self.maxbuf = maxbuf

    def handle(self):
        while True:
            try:
                rlist = []
                wlist = []
                xlist = [self.a, self.b]
                if self.atob:
                    wlist.append(self.b)
                if self.btoa:
                    wlist.append(self.a)
                if len(self.atob) < self.maxbuf:
                    rlist.append(self.a)
                if len(self.btoa) < self.maxbuf:
                    rlist.append(self.b)
                rlo, wlo, xlo = select(rlist, wlist, xlist)
                if xlo:
                    return
                if self.a in wlo:
                    n = self.a.send(self.btoa)
                    self.btoa = self.btoa[n:]
                if self.b in wlo:
                    n = self.b.send(self.atob)
                    self.atob = self.atob[n:]
                if self.a in rlo:
                    s = self.a.recv(self.maxbuf - len(self.atob))
                    if not s:
                        return
                    self.atob += s
                if self.b in rlo:
                    s = self.b.recv(self.maxbuf - len(self.btoa))
                    if not s:
                        return
                    self.btoa += s
            except ConnectionResetError:
                return


class TCPRelay(socketserver.BaseRequestHandler):
    def handle(self):
        logger = Logger(self.server.args)
        logger.debug(f"Incoming connection to {self.server.server_address[1]}")
        mux = USBMux(self.server.socketpath)
        logger.debug("Waiting for devices...")
        if not mux.devices:
            mux.process(1.0)
        if not mux.devices:
            logger.debug("No device found")
            self.request.close()
            return
        dev = mux.devices[0]
        logger.debug(f"Connecting to device {str(dev)}")
        dsock = mux.connect(dev, self.server.server_address[1])
        lsock = self.request
        logger.debug("Connection established, relaying data")
        try:
            fwd = SocketRelay(dsock, lsock, 131072)
            fwd.handle()
        finally:
            dsock.close()
            lsock.close()
        logger.debug("Connection closed")


class TCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class Relayer(object):
    def __init__(self, rport, lport, args, host=None, socketpath=None):
        self.rport = rport
        self.lport = lport
        self.args = args
        if host is None:
            host = 'localhost'
        self.host = host
        if socketpath is None:
            socketpath = '/var/run/usbmuxd'
        self.socketpath = socketpath
        self.logger = Logger(self.args)

    def relay(self):
        self.logger.log(f"Forwarding local port {self.lport} to remote port {self.rport}", color=Colors.pink)
        server = TCPServer((self.host, self.lport), TCPRelay)
        server.rport = self.rport
        server.socketpath = self.socketpath
        server.args = self.args
        servers = [server]

        alive = True

        while alive:
            try:
                rl, wl, xl = select(servers, [], [])
                for serv in rl:
                    serv.handle_request()
            except:
                alive = False
