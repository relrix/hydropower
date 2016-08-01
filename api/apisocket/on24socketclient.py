"""clinet socket to start process.

Copyright (C) 2016 - Shishir Pokharel
shishir.pokharel@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import socket
import json


class StartProcessClient ():
    """StartProcessClient class will just send processs start command to StartProcessServer."""

    _BUFF_SIZE = 1024
    _END_BYTES = "ON24EOS"
    _PORT = 23000

    def send_message(self, server, message):
        """send message to app and get response end message by <space><space>EOS."""
        try:
            self.server = server
            self.response = {"status": "null", "message": "null"}
            self.data = ''
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(20)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print "connecting to server on port " + str(self._PORT)
            self.socket.connect((self.server, self._PORT))
        except:
            print "Error Occurred"
            return self.response_2_api_req("failed", "Cannot send message to start process on port " + str(self._PORT))

        print "sending " + message
        self.socket.sendall(message)
        while self._END_BYTES not in self.data:
            try:
                _buffer = self.socket.recv(self._BUFF_SIZE)
                print "Received data is " + _buffer
                self.data += _buffer

                if not _buffer:
                    print "No data received destory connection"
                    break

            except socket.timeout:
                print "Timeout occurred"
                self.socket.close()
                return self.response_2_api_req("failed", "timeout occurred on port " + str(self._PORT))

            else:
                socketmsg = json.loads(self.data)
                return self.response_2_api_req(socketmsg["status"], socketmsg["message"])

            print "closing socket for api"
            self.socket.close()
            return self.response

    def response_2_api_req(self, status, message):
        """send response to api call."""
        response = {}
        response["status"] = status
        response["message"] = message
        return response


def client_start_process(server, message):
    """Get server and message and send the response back."""
    proc = StartProcessClient()
    dict_message = proc.send_message(server, message)
    return dict_message


# if __name__ == '__main__':
#     message = json.dumps({'eventid': '12345', 'action': 'start', 'on24data': 'ON24EOS'}, separators=(',', ':'))
#     response = client_start_process('127.0.0.1', message)
#     print "response " + str(response)
