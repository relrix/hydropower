"""server socket.

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
from threading import Thread
# import time
import sys
import json

# from CodernityDB.database import Database
# from CodernityDB.hash_index import HashIndex

from CodernityDB.database_thread_safe import ThreadSafeDatabase
from CodernityDB.database import RecordNotFound


# import sys

class on24localDB(object):
    """code to insert port in db. Only On24SocketServer will run this file."""

    # not from root path because On24SocketServer will run this file
    _DATABASE = '../db/database'

    @classmethod
    def delete_data(cls, eventid):
        """delete data."""
        cdb = ThreadSafeDatabase(cls._DATABASE)
        status = False
        if cdb.exists():
            cdb.open()
            cdb.reindex()
        try:
            record_dict = cdb.get('eventid', eventid, with_doc=True, with_storage=True)
            record = record_dict['doc']
            cdb.delete({'_id': record['_id'], '_rev': record['_rev']})
            status = True
        except RecordNotFound:
            print "Record not Found"
            status = False
        except:
            print "Error"
            status = False
        finally:
            cdb.close()
            return status

    @classmethod
    def insert_data(cls, eventid, key, value):
        """insert data."""
        cdb = ThreadSafeDatabase(cls._DATABASE)
        status = False
        if cdb.exists():
            cdb.open()
            cdb.reindex()
        try:
            record_dict = cdb.get('eventid', eventid, with_doc=True, with_storage=False)
            record = record_dict['doc']
            cdb.update({key: value, "server": record['server'], "eventid": eventid, '_id': record['_id'], '_rev': record['_rev']})
            status = True
        except RecordNotFound:
            status = False
        except:
            status = False
        finally:
            cdb.close()
            return status

    @classmethod
    def get_data(cls, eventid, key):
        """get data."""
        cdb = ThreadSafeDatabase(cls._DATABASE)
        return_data = None
        if cdb.exists():
            cdb.open()
            cdb.reindex()
        try:
            print eventid
            record_dict = cdb.get('eventid', eventid, with_doc=True, with_storage=True)
            print record_dict
            record = record_dict['doc']
            return_data = record[key]
            print record
        except RecordNotFound:
            print "Record not Found"
            return_data = None
        except:
            print "Error"
            return_data = None
        finally:
            cdb.close()
            return return_data


class ServerListener(Thread):
    """Listener class."""

    __BUFF_SIZE = 1024
    # __END_BYTES = '\x20\x20\x45\x4F\x53\r'
    __END_BYTES = "ON24EOS"

    def __init__(self, eventid, _callback):
        """initialize."""
        Thread.__init__(self)
        self.eventid = eventid
        self.server = ''
        self.port = ''
        self.socket = ''
        self.running = True
        self._callback = _callback

    @property
    def callback(self):
        """Getter for callback."""
        return self._callback

    @callback.setter
    def callback(self, value):
        """Setter for callback."""
        self._callback = value

    @callback.deleter
    def callback(self):
        """Delete callback."""
        del self._callback

    def stop(self):
        """stop thread."""
        print "set stop param"
        try:
            self.running = False
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client_socket.connect((self.server, self.port))
            client_socket.sendall({'on24data': self.__END_BYTES})
        except:
            print "Error while stopping listener"

        try:
            on24localDB.delete_data(self.eventid)
        except:
            print "Error while deleting data from db."

    def run(self):
        """listen to locahost on supplied port."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "server listening ..."
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((on24localDB.get_data(self.eventid, 'server'), 0))
        self.server, self.port = self.socket.getsockname()
        on24localDB.insert_data(self.eventid, 'port', self.port)

        self.socket.listen(1)

        while self.running:
            print "waiting for incoming connection..."
            data = ''
            try:
                connection, client_address = self.socket.accept()
                print "connected from " + str(client_address)
                while self.__END_BYTES not in data:
                    try:
                        _buffer = connection.recv(self.__BUFF_SIZE)
                        data += _buffer
                        if not _buffer:
                            print "No data received disconnect client"
                            data = None
                            break
                    except:
                        self.response_2_api_req(connection, "failed", "Didn't received bytes from client " + str(client_address))
                        data = None

                if data:
                    socketmsg = json.loads(data)
                    print socketmsg
                    mmssgg = self._callback(socketmsg)
                    print mmssgg
                    self.response_2_api_req(connection, "success", "callback return data goes here ")
            #except:
            #    if connection is not None:
            #        self.response_2_api_req(connection, "failed", "App cannot connect with api client socket")

            finally:
                if connection is not None:
                    connection.close()
                    print "Closing connection with API APP socket"

        print "Quiting socket Listener"
        self.socket.close()

    def response_2_api_req(self, connection, status, message):
        """send response to api call."""
        if connection is not None:
            socketresponse = {}
            socketresponse["status"] = status
            socketresponse["message"] = message
            socketresponse["on24data"] = "ON24EOS"
            response = json.dumps(socketresponse, separators=(',', ':'))
            connection.sendall(response)

#
# def socket_start_listener(eventid):
#     """function which will create class."""
#     listen = ServerListener(eventid)
#     listen.start()
#     # print "sleeping now"
#     # time.sleep(10)
#     # print "sending stop now"
#     # listen.stop()
#
# if __name__ == '__main__':
#     param = str(sys.argv[1])
#     if param.isdigit():
#         socket_start_listener(param)
