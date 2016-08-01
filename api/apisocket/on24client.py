"""client socket.

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
# import re
import json
# import sys


class ProcessCommunicator ():
    """Process communication class accept port and message and comminucates with app."""

    _BUFF_SIZE = 1024
    # _END_BYTES = '\x20\x20\x45\x4F\x53\r'
    _END_BYTES = "ON24EOS"

    def send_message(self, port, message):
        """send message to app and get response end message by <space><space>EOS."""
        try:
            self.server = '127.0.0.1'
            self.data = ''
            self.response = {}
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(20)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print "connecting to server on port " + str(port)
            self.socket.connect((self.server, port))
        except:
            print "Error Occurred"
            return self.response_2_api_req("failed", "not able to connect on socket at port " + str(port))

        try:
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
                    return self.response_2_api_req("failed", "timeout occurred on port " + str(port))
        except:
            print "Error Occurred."
            self.socket.close()
            return self.response_2_api_req("failed", "Error while sending message on port " + str(port))
        else:
            socketmsg = json.loads(self.data)
            self.socket.close()
            return self.response_2_api_req(socketmsg["status"], socketmsg["message"])

        # finally:
        #     print "finally closing socket."
        #     self.socket.close()
        #     return self.response

    def response_2_api_req(self, status, message):
        """send response to api call."""
        response = {}
        response["status"] = status
        response["message"] = message
        return response


def socket_get_dict_response(port, message):
    """Get port and message and send the response back."""
    proc = ProcessCommunicator()
    dict_message = proc.send_message(port, message)
    return dict_message


# if __name__ == '__main__':
#    response = socket_get_dict_response(35350, "Hi shishir !!!!")
#    print "response " + str(response)
