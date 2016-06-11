"""impoundment.

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
import collections


class impoundment():
    """impoundment class."""

    def __init__(self):
        """initialize sinks."""
        self.sinks = {}
        for i in range(9):
            self.sinks["sink_" + str(i)] = {}
            if i == 0:
                self.sinks["sink_" + str(i)]["xpos"] = 0
                self.sinks["sink_" + str(i)]["ypos"] = 0
                self.sinks["sink_" + str(i)]["linked"] = False
            if i == 1:
                self.sinks["sink_" + str(i)]["xpos"] = 480
                self.sinks["sink_" + str(i)]["ypos"] = 20
                self.sinks["sink_" + str(i)]["linked"] = False
            elif i == 2:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
                self.sinks["sink_" + str(i)]["linked"] = False
            elif i == 3:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
                self.sinks["sink_" + str(i)]["linked"] = False
            elif i == 4:
                self.sinks["sink_" + str(i)]["xpos"] = 20
                self.sinks["sink_" + str(i)]["ypos"] = 20
                self.sinks["sink_" + str(i)]["linked"] = False
            elif i == 5:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
                self.sinks["sink_" + str(i)]["linked"] = False
            elif i == 6:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
                self.sinks["sink_" + str(i)]["linked"] = 0
            elif i == 7:
                self.sinks["sink_" + str(i)]["xpos"] = 200
                self.sinks["sink_" + str(i)]["ypos"] = 260
                self.sinks["sink_" + str(i)]["linked"] = False
            elif i == 8:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"] + 160
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"]
                self.sinks["sink_" + str(i)]["linked"] = False

    def get_all_sinks(self):
        """get all sinks."""
        return collections.OrderedDict(sorted(self.sinks.items()))

    def get_sink_location(self, sink_name):
        """get sink."""
        self.set_sink(sink_name, True)
        return self.sinks[sink_name]

    def set_sink(self, sink_name, state):
        """set sink."""
        if self.sinks[sink_name]["linked"] == state:
            raise Exception('sink already in use')
        else:
            self.sinks[sink_name]["linked"] = state
            return True


# def init():
#     """init."""
#    impoundmentObj = impoundment()
#    print impoundmentObj.get_all_sinks()
    # return impoundmentObj
    # obj.get_sink_location("sink_4")
#     sinks = obj.get_all_sinks()
#     for c in collections.OrderedDict(sorted(sinks.items())):
#         print c, sinks[c]
#     obj.set_sink("sink_4", False)
#     for c in collections.OrderedDict(sorted(sinks.items())):
#         print c, sinks[c]
#
# init()
