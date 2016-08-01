#!/usr/bin/python
"""hydropower.

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
from headwater import powerhouse as mainapp
from threading import Thread
import sys
import time
import signal
import api.apisocket.on24server as appsocket


class mainClass():
    """main class."""

    def __init__(self, eventdid, dsturl):
        """init."""
        self.eventid = eventid
        self.dsturl = dsturl
        self.infinite_loop = True
        self.myapp = None
        self.on24sock = None

    def start_engine(self):
        """start engine."""
        print "Kick started the engine."
        self.myapp = mainapp.powerhouse(self.dsturl)
        self.on24sock = appsocket.ServerListener(eventid, self.callback1)
        self.on24sock.start()
        self.myapp.start()

    def callback1(self, message):
        """my callback."""
        if message['action'] == 'add_presenter':
            self.myapp.addVideoTiles(message['rtmpurl'] + " live=1", message['presenter_id'])
        elif message['action'] == 'switch_presenter':
            self.myapp.changeStream(message['presenter_id'])
        print " I have a callback to deal with"
        return "you got it! "

    def usr_signal(self, signum, stack):
        """handel User Signal."""
        print 'Received UserSIG:', signum
        self.on24sock.stop()
        self.myapp.stop()
        self.infinite_loop = False

    def child_signal(self, signum, stack):
        """handel Ctrl+C."""
        print 'Received:', signum
        self.on24sock.stop()
        self.myapp.stop()
        self.infinite_loop = False

    def go_infinite(self):
        """listen when to self destory."""
        while(self.infinite_loop):
            try:
                print "waiting for self destruction"
                time.sleep(3)
            except KeyboardInterrupt:
               break

        self.myapp.join()
        self.on24sock.join()
        print "END OF APP."
        sys.exit(0)


if __name__ == '__main__':
    eventid = str(sys.argv[1])
    dsturl = str(sys.argv[2])
    listen = mainClass(eventid, dsturl)
    signal.signal(signal.SIGINT, listen.child_signal)
    signal.signal(signal.SIGUSR1, listen.usr_signal)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    listen.start_engine()
    listen.go_infinite()
