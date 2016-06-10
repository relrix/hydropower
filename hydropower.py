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
from headwater import powerhouse
from threading import Thread
import time
import random

hydroObj = powerhouse.powerhouse()
hydroObj.tailrace()


def threadStart(hydro_obj):
    """thread."""
    print "Running on the thread"
    count = 0
    val = 0
    while(count <= 0):
        val = random.randinit(10, 60)
        val = val + 10
        print "sleeping " + str(val) + " seconds"
        time.sleep(val)
        if count % 2 == 0:
            hydro_obj.add_streams("RTMPURL")
        else:
            hydro_obj.add_streams("RTMPURL")
        count = count + 1


testThread = Thread(target=threadStart, args=(hydroObj,))
testThread.start()

hydroObj.addstream("ADD Main stream")
