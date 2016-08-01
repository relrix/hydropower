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
                self.sinks["sink_" + str(i)]["presenter_id"] = -1
                self.sinks["sink_" + str(i)]["zorder"] = 1
            if i == 1:
                self.sinks["sink_" + str(i)]["xpos"] = 480
                self.sinks["sink_" + str(i)]["ypos"] = 20
                self.sinks["sink_" + str(i)]["presenter_id"] = 0
                self.sinks["sink_" + str(i)]["zorder"] = 3
            elif i == 2:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
                self.sinks["sink_" + str(i)]["presenter_id"] = 0
                self.sinks["sink_" + str(i)]["zorder"] = 4
            elif i == 3:
                self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
                self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
                self.sinks["sink_" + str(i)]["presenter_id"] = 0
                self.sinks["sink_" + str(i)]["zorder"] = 5
            elif i == 4:
                self.sinks["sink_" + str(i)]["xpos"] = 20
                self.sinks["sink_" + str(i)]["ypos"] = 20
                self.sinks["sink_" + str(i)]["presenter_id"] = 0
                self.sinks["sink_" + str(i)]["zorder"] = 6
            # elif i == 5:
            #     self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
            #     self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
            #     self.sinks["sink_" + str(i)]["presenter_id"] = 0
            # elif i == 6:
            #     self.sinks["sink_" + str(i)]["xpos"] = self.sinks["sink_" + str(i - 1)]["xpos"]
            #     self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"] + 100
            #     self.sinks["sink_" + str(i)]["presenter_id"] = 0
            # elif i == 7:
            #     self.sinks["sink_" + str(i)]["xpos"] = 356
            #     self.sinks["sink_" + str(i)]["ypos"] = self.sinks["sink_" + str(i - 1)]["ypos"]
            #     self.sinks["sink_" + str(i)]["presenter_id"] = 0
            # elif i == 8:
            #     self.sinks["sink_" + str(i)]["xpos"] = 300
            #     self.sinks["sink_" + str(i)]["ypos"] = 260
            #     self.sinks["sink_" + str(i)]["presenter_id"] = 0

    def get_all_sinks(self):
        """get all sinks."""
        return collections.OrderedDict(sorted(self.sinks.items()))

    def get_sink_location(self, sink_name, presenter_id):
        """get sink."""
        self.set_sink(sink_name, presenter_id)
        return self.sinks[sink_name]

    def set_sink(self, sink_name, presenter_id):
        """set sink."""
        if not presenter_id or presenter_id < 1:
            raise Exception('presenter is mising')
        else:
            self.sinks[sink_name]["presenter_id"] = presenter_id
