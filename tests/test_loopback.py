import socket
import threading
import unittest

from serve_fixture import Server, IAC, DO, GMCP, MSDP


class LoopbackTests(unittest.TestCase):
    def test_local_negotiation_and_partial_payload(self):
        with Server() as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                self.assertEqual(server.server_address[0], '127.0.0.1')
                with socket.create_connection(server.server_address, timeout=2) as client:
                    greeting = b''
                    while not greeting.endswith(b'\r\n'):
                        greeting += client.recv(2048)
                    self.assertIn(b'Toolbox loopback fixture', greeting)
                    client.sendall(bytes([IAC, DO, GMCP, IAC, DO, MSDP]) + b'partial\r\n')
                    result = b''
                    while b'\x01HEALTH\x0210\xff\xf0' not in result:
                        result += client.recv(2048)
                    self.assertIn(b'Toolbox score: 42\r\n', result)
                    self.assertIn(b'Char.Vitals {"hp": "10"}', result)
                    self.assertNotIn(b'maxhp', result)
            finally:
                server.shutdown()
                thread.join(2)


if __name__ == '__main__':
    unittest.main()
