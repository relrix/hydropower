"""Stream Class.

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
from audiostream import get_bin_pad
import gi
gi.require_version('Gst', '1.0')
GObject.threads_init()
Gst.init(None)


class InputBin():
    """InputBin."""

    def __init__(self, pipeline, mixer_pad, rtmp_location, flvmuxer, tile):
        """init."""
        self.pipeline = pipeline
        self.mixer_pad = mixer_pad
        self.rtmp_location = rtmp_location
        self.flvmuxer = flvmuxer
        self.tile = tile
        self.CustomBin = Gst.Bin.new(None)

    def get_ghost_pad(self):
        """create Element Factory."""
        self.videosrc = Gst.ElementFactory.make("rtmpsrc", None)
        self.decodebin = Gst.ElementFactory.make("decodebin", None)
        self.decodevidqueue = Gst.ElementFactory.make("queue", None)
        self.videoscale = Gst.ElementFactory.make("videoscale", None)
        self.videorate = Gst.ElementFactory.make("videorate", None)
        self.videocaps = Gst.ElementFactory.make("capsfilter", None)
        self.videoconvert = Gst.ElementFactory.make("videoconvert", None)
        self.videosinkqueue = Gst.ElementFactory.make("queue", None)

        if not self.videosrc or not self.decodebin or not self.decodevidqueue or not self.videoscale or not self.videorate \
                or not self.videocaps or not self.videoconvert or not self.videosinkqueue:
            raise Exception('Cannot create all gst element')

        """set properties."""

        self.videosrc.set_property("location", self.rtmp_location)
        # self.videosrc.set_property("do-timestamp", True)
        self.videosrc.set_property("blocksize", 1024)
        self.decodebin.set_property("message-forward", "true")
        self.decodebin.connect('pad-added', self.on_pad_added)
        self.videoscale.set_property("method", "bilinear")
        self.videocaps.set_property("caps", Gst.Caps.from_string(get_video_caps(self.tile)))

        """add elements to CustomBin."""

        for element in (self.videosrc, self.decodebin, self.decodevidqueue, self.videoscale, self.videorate, self.videocaps, self.videoconvert, self.videosinkqueue):
            self.CustomBin.add(element)

        """link elements to CustomBin."""

        self.videosrc.link(self.decodebin)
        self.decodebin.link(self.decodevidqueue)
        self.decodevidqueue.link(self.videoscale)
        self.videoscale.link(self.videorate)
        self.videorate.link(self.videocaps)
        self.videocaps.link(self.videoconvert)
        self.videoconvert.link(self.videosinkqueue)
        Connectpad = self.videosinkqueue.get_static_pad("src")
        ghostPad = Gst.GhostPad.new(None, Connectpad)
        self.CustomBin.add_pad(ghostPad)

        clock = self.pipeline.get_clock()
        self.CustomBin.set_base_time(self.pipeline.get_base_time())
        self.CustomBin.set_clock(clock)
        if not self.tile:
            self.CustomBin.set_state(Gst.State.READY)
        # else:
        #    self.CustomBin.set_state(Gst.State.PLAYING)
        if self.tile:
            ghostPad.add_probe(Gst.PadProbeType.BUFFER, self.buff_event, None)

        return self.CustomBin, ghostPad

    def on_pad_added(self, element, pad):
        """Callback to link a/v sink to decoder source."""
        string = pad.query_caps(None).to_string()

        if string.startswith('video/'):
            pad.link(self.decodevidqueue.get_static_pad('sink'))
        elif string.startswith('audio/') and self.tile:
            audiobin, audqueuesink, audioelement = get_bin_pad(self.pipeline, self.decoder, self.tile)
            pad.link(audqueuesink)
            if self.tile:
                audioelement.link(self.flvmuxer)

    def elements_changestate(self):
        """Change state to playing."""
        self.CustomBin.set_state(Gst.State.PLAYING)

    def buff_event(self, pad, info, user_data):
        """block start segment."""
        buf = info.get_buffer()
        # print("before BUFF PTS = %f  DTS %f duration %f " %(buf.pts,buf.dts,buf.duration))
        clock = Gst.SystemClock.obtain()
        buf.pts = clock.get_time() - self.pipeline.get_base_time() + buf.duration
        buf.dts = clock.get_time() - self.pipeline.get_base_time() - buf.duration
        # print("after BUFF PTS = %f  DTS %f duration %f " %(buf.pts,buf.dts,buf.duration))
        return Gst.PadProbeReturn.OK


def get_video_caps(tile=True):
    """get vidoe caps."""
    if not tile:
        return "video/x-raw,framerate=12/1,format=I420,width=640,height=360"
    else:
        return "video/x-raw,framerate=12/1,format=I420,width=146,height=90"


def get_stream_for_mix(pipeline=None, mixer_pad=None, rtmpsrc=None, flvmuxer=None, tile=True):
    """Get required param to create a bin."""
    if not rtmpsrc or not pipeline or not mixer_pad or not flvmuxer:
        raise Exception('Mandotarty fields are missing')
    bin = InputBin(pipeline, mixer_pad, rtmpsrc, flvmuxer, tile)
    custom_bin, pad = bin.get_ghost_pad()
    return custom_bin, pad
