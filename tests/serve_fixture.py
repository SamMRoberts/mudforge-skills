#!/usr/bin/env python3
"""Disposable loopback-only Telnet/GMCP/MSDP peer; never contacts a real MUD."""

import argparse
import json
import socketserver

IAC, WILL, WONT, DO, DONT, SB, SE = 255, 251, 252, 253, 254, 250, 240
GMCP, MSDP = 201, 69


def frame(option, data):
    return bytes([IAC, SB, option]) + data.replace(b'\xff', b'\xff\xff') + bytes([IAC, SE])


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(300)
        self.gmcp = False
        self.msdp = False
        self.state = 'data'
        self.negotiation = None
        self.line = bytearray()
        self.request.sendall(bytes([IAC, WILL, GMCP, IAC, WILL, MSDP]) +
                             b'Toolbox loopback fixture. Type fixture or partial.\r\n')
        try:
            while data := self.request.recv(2048):
                for byte in data:
                    self.consume(byte)
        except (OSError, ConnectionError):
            return

    def consume(self, byte):
        if self.state == 'option':
            enabled = self.negotiation == DO
            if byte == GMCP:
                self.gmcp = enabled
            elif byte == MSDP:
                self.msdp = enabled
            self.state = 'data'
        elif self.state == 'sub':
            if byte == IAC:
                self.state = 'sub-iac'
        elif self.state == 'sub-iac':
            self.state = 'data' if byte == SE else 'sub'
        elif self.state == 'iac':
            if byte in (DO, DONT, WILL, WONT):
                self.negotiation = byte
                self.state = 'option'
            elif byte == SB:
                self.state = 'sub'
            else:
                self.state = 'data'
        elif byte == IAC:
            self.state = 'iac'
        elif byte == 10:
            self.command(bytes(self.line).decode('ascii', errors='replace').strip())
            self.line.clear()
        elif byte != 13:
            if len(self.line) >= 512:
                raise ConnectionError('fixture input limit')
            self.line.append(byte)

    def command(self, command):
        if command not in ('fixture', 'partial', 'invalid'):
            self.request.sendall(b'Local commands: fixture, partial, invalid.\r\n')
            return
        payload = {'hp': '25', 'maxhp': '100'}
        if command == 'partial':
            payload = {'hp': '10'}
        elif command == 'invalid':
            payload = {'hp': 'invalid', 'maxhp': '0'}
        result = b'Toolbox score: 42\r\n'
        if self.gmcp:
            result += frame(GMCP, b'Char.Vitals ' + json.dumps(payload).encode())
        if self.msdp:
            result += frame(MSDP, b'\x01HEALTH\x02' + payload['hp'].encode())
            if 'maxhp' in payload:
                result += frame(MSDP, b'\x01HEALTH_MAX\x02' + payload['maxhp'].encode())
        self.request.sendall(result)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, port=0):
        super().__init__(('127.0.0.1', port), Handler)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=0)
    args = parser.parse_args()
    with Server(args.port) as server:
        print(json.dumps({'host': '127.0.0.1', 'port': server.server_address[1],
                          'commands': ['fixture', 'partial', 'invalid']}), flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
