"""Audio Stream Class.

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

from gi.repository import GObject
from gi.repository import Gst
import gi
gi.require_version('Gst', '1.0')
GObject.threads_init()
Gst.init(None)


class audiobin():
    """audiobin."""

    def __init__(self, pipeline, demuxer, tile):
        """init."""
        self.pipeline = pipeline
        self.demuxer = demuxer
        self.tile = tile
        self.AudioBin = Gst.Bin.new(None)

    def get_audio_ghost_pad(self):
        """create Element Factory."""
        self.decodeaudqueue = Gst.ElementFactory.make("queue", None)
        self.audioconvert = Gst.ElementFactory.make("audioconvert", None)
        self.audioresample = Gst.ElementFactory.make("audioresample", None)
        self.audiorate = Gst.ElementFactory.make("audiorate", None)
        self.audiocaps = Gst.ElementFactory.make("capsfilter", None)
        self.aacencode = Gst.ElementFactory.make("avenc_aac", None)
        self.audiosinkqueue = Gst.ElementFactory.make("queue", None)

        if not self.decodeaudqueue or not self.audioconvert or not self.audioresample or not self.audiorate or not self.audiocaps \
                or not self.aacencode or not self.audiosinkqueue:
            raise Exception('Cannot create all audio bin ')

        """set properties."""
        self.audiocaps.set_property("caps", Gst.Caps.from_string("audio/x-raw, rate=44100"))
        self.aacencode.set_property("compliance", -2)

        """add elements to audiobin."""
        for element in (self.decodeaudqueue, self.audioconvert, self.audioresample, self.audiorate, self.audiocaps, self.aacencode, self.audiosinkqueue):
            self.AudioBin.add(element)

        """link elements to audiobin."""
        self.demuxer.link(self.decodeaudqueue)
        self.decodeaudqueue.link(self.audioconvert)
        self.audioconvert.link(self.audioresample)
        self.audioresample.link(self.audiorate)
        self.audiorate.link(self.audiocaps)
        self.audiocaps.link(self.aacencode)
        self.aacencode.link(self.audiosinkqueue)

        """create a ghost pad for audiobin."""

        Connectpadsink = self.decodeaudqueue.get_static_pad("sink")
        Connectpadsrc = self.audiosinkqueue.get_static_pad("src")
        ghostPadsink = Gst.GhostPad.new(None, Connectpadsink)
        ghostPadsrc = Gst.GhostPad.new(None, Connectpadsrc)
        self.AudioBin.add_pad(ghostPadsink)
        self.AudioBin.add_pad(ghostPadsrc)

        clock = self.pipeline.get_clock()
        self.AudioBin.set_base_time(self.pipeline.get_base_time())
        self.AudioBin.set_clock(clock)
        if not self.tile:
            self.CustomBin.set_state(Gst.State.READY)
        # else:
        #    self.CustomBin.set_state(Gst.State.PLAYING)
        if self.tile:
            ghostPadsrc.add_probe(Gst.PadProbeType.BUFFER, self.buff_event, None)

        return self.AudioBin, ghostPadsink, ghostPadsrc

    def buff_event(self, pad, info, user_data):
        """block  buffer and change PTS / DTS."""
        buf = info.get_buffer()
        # print("before BUFF PTS = %f  DTS %f duration %f " %(buf.pts,buf.dts,buf.duration))
        clock = Gst.SystemClock.obtain()
        buf.pts = clock.get_time() - self.pipeline.get_base_time() + buf.duration
        buf.dts = clock.get_time() - self.pipeline.get_base_time() - buf.duration
        # print("after BUFF PTS = %f  DTS %f duration %f " %(buf.pts,buf.dts,buf.duration))
        return Gst.PadProbeReturn.OK


def get_bin_pad(pipeline=None, demuxer=None, tile=True):
    """Get required param to create a bin."""
    if not pipeline or not demuxer:
        raise Exception('Mandotarty fields are missing fro audio bin')
    bin = audiobin(pipeline, demuxer, tile)
    audio_bin, ghostpadsink, ghostpadsrc = bin.get_audio_ghost_pad()
    return audio_bin, ghostpadsink, ghostpadsrc
