"""server socket to fork and start process.

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
import signal
import json
from subprocess import Popen
import os
import sys
import fcntl


class StartProcessServer():
    """StartProcessServer class will fork a child and swapn process."""

    _BUFF_SIZE = 1024
    _END_BYTES = "ON24EOS"

    def __init__(self, server, port):
        """initialize."""
        self.server = server
        self.port = port
        self.running = True

    def stop(self):
        """stop thread."""
        print "Got close signal."
        try:
            self.running = False
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            client_socket.connect((self.server, self.port))
            client_socket.sendall({'on24data': self.__END_BYTES})
        except:
            print "Error while stopping listener"

    def run(self):
        """listen to locahost on supplied port."""
        listenersocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Server Started ..."
        listenersocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listenersocket.bind((self.server, self.port))
        listenersocket.listen(1)
        self.prevent_socket_inheritance(listenersocket)

        while self.running:
            print "waiting for incoming connection..."
            data = ''
            try:
                connection = None
                connection, client_address = listenersocket.accept()
                print "Client connected on port " + str(client_address)
                while self._END_BYTES not in data:
                    try:
                        _buffer = connection.recv(self._BUFF_SIZE)
                        print _buffer
                        data += _buffer
                        if not _buffer:
                            print "No data received disconnect client"
                            data = None
                            break
                    except:
                        self.send_response_2_socket(connection, "failed", "Didn't received bytes from clinet on port " + str(self.port))
                        data = None

                if data:
                    socketmsg = json.loads(data)

                    if(socketmsg['action'] == 'startProcess'):
                        try:
                            newpid = os.fork()
                            # CHILD
                            if newpid == 0:
                                self.running = False
                                FNULL = open("/tmp/log." + socketmsg['eventid'], 'wb')
                                Popen(["python", "/usr/local/gst/webcam/hydropower/hydropower.py", socketmsg['eventid'] , socketmsg['rtmpurldst']], stdout=FNULL, stderr=FNULL).pid
                                # time.sleep(2)

                        except:
                            self.send_response_2_socket(connection, "failed", "Error starting Encodeer Process.")
                        else:
                            print "Child process forked"
                            self.send_response_2_socket(connection, "success", "Encoder app started")

            except KeyError:
                print "no key action found"
                self.send_response_2_socket(connection, "failed", "api call not valid - no action key found.")

            except:
                if connection is not None:
                    self.send_response_2_socket(connection, "failed", "Server cannot connect with api client on port " + str(self.port))

            finally:
                if connection is not None:
                    connection.close()
                    print "connection closed with client"

        print "closing main loop for connnection listener"
        listenersocket.close()
        sys.exit(0)

    def send_response_2_socket(self, connection, status, message):
        """send response to api call."""
        if connection is not None:
            socketresponse = {}
            socketresponse["status"] = status
            socketresponse["message"] = message
            socketresponse["on24data"] = "ON24EOS"
            response = json.dumps(socketresponse, separators=(',', ':'))
            connection.sendall(response)

    def usr_signal(self, signum, stack):
        """handel User Signal."""
        print 'Received UserSIG:', signum
        self.stop()

    def child_signal(self, signum, stack):
        """handel Ctrl+C."""
        print 'Received:', signum
        self.stop()

    def prevent_socket_inheritance(self, sock):
        """Mark the given socket fd as non-inheritable (POSIX)."""
        fd = sock.fileno()
        old_flags = fcntl.fcntl(fd, fcntl.F_GETFD)
        fcntl.fcntl(fd, fcntl.F_SETFD, old_flags | fcntl.FD_CLOEXEC)

if __name__ == '__main__':
    listen = StartProcessServer('127.0.0.1', 23000)
    signal.signal(signal.SIGINT, listen.child_signal)
    signal.signal(signal.SIGUSR1, listen.usr_signal)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    listen.run()
