"""Base Stream Template Class.

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
# GObject.threads_init()
# Gst.init(None)


class avbin():
    """audio video bin."""

    def __init__(self, pipeline, video_mixer_pad, audio_mixer_pad):
        """init."""
        self.pipeline = pipeline
        self.mixer_pad = video_mixer_pad
        self.audio_mixer_pad = audio_mixer_pad # request realease not yet implemented
        self.VideoTemplateBin = Gst.Bin.new(None)
        self.AudioTemplateBin = Gst.Bin.new(None)

    def get_connect_pads(self):
        """create Element Factory.

        return self.VideoTemplateBin, self.AudioTemplateBin, ghostPad, ghostPad1
        """
        videosrc = Gst.ElementFactory.make("videotestsrc", None)
        videocaps = Gst.ElementFactory.make("capsfilter", None)
        videoconvert = Gst.ElementFactory.make("videoconvert", None)
        videosinkqueue = Gst.ElementFactory.make("queue", None)

        audiosrc = Gst.ElementFactory.make("audiotestsrc", None)
        audiocaps = Gst.ElementFactory.make("capsfilter", None)
        audioconvert = Gst.ElementFactory.make("audioconvert", None)
        audiosinkqueue = Gst.ElementFactory.make("queue", None)

        if not videosrc or not videocaps or not videoconvert or not videosinkqueue or not audiosrc \
                or not audiocaps or not audioconvert or not audiosinkqueue:
            raise Exception('Cannot create all gst element')

        """set properties."""

        videosrc.set_property("pattern", 18)
        videosrc.set_property("is-live", True)

        audiosrc.set_property("wave", 4)
        audiosrc.set_property("is-live", True)
        audiosrc.set_property("volume", 0.1)

        # videosrc.set_property("do-timestamp", True)
        # videosrc.set_property("blocksize", 512)
        videocaps.set_property("caps", Gst.Caps.from_string("video/x-raw,framerate=30/1,format=I420,width=640,height=360"))
        audiocaps.set_property("caps", Gst.Caps.from_string("audio/x-raw, format=S16LE, rate=44100, channels=2, layout=interleaved"))

        """add elements to pipeline."""

        for element in (videosrc, videocaps, videoconvert, videosinkqueue):
            self.VideoTemplateBin.add(element)

        for element in (audiosrc, audiocaps, audioconvert, audiosinkqueue):
            self.AudioTemplateBin.add(element)

        """link elements to CustomBin."""

        videosrc.link(videocaps)
        videocaps.link(videoconvert)
        videoconvert.link(videosinkqueue)

        audiosrc.link(audiocaps)
        audiocaps.link(audioconvert)
        audioconvert.link(audiosinkqueue)

        VideoConnectpad = videosinkqueue.get_static_pad("src")
        ghostPad = Gst.GhostPad.new(None, VideoConnectpad)
        self.VideoTemplateBin.add_pad(ghostPad)

        AudioConnectpad = audiosinkqueue.get_static_pad('src')
        ghostPad1 = Gst.GhostPad.new(None, AudioConnectpad)
        self.AudioTemplateBin.add_pad(ghostPad1)

        self.pipeline.add(self.VideoTemplateBin)
        self.pipeline.add(self.AudioTemplateBin)

        # ghostPad1.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.eos_event, None)

        ghostPad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.eos_event, None)

        return self.VideoTemplateBin, self.AudioTemplateBin, ghostPad, ghostPad1

    def eos_event(self, pad, info, user_data):
        """on EOS EVENT."""
        EventType = info.get_event().type
        print str(EventType) + " _____VIDEO_____"
        if(EventType == Gst.EventType.EOS):
            print("End-Of-Stream reached. VIDEO")
            self.VideoTemplateBin.set_state(Gst.State.NULL)
            self.AudioTemplateBin.set_state(Gst.State.NULL)
            self.pipeline.remove(self.VideoTemplateBin)
            self.pipeline.remove(self.AudioTemplateBin)
            # TODO do clean ups for later

            self.videomix.release_request_pad(self.mixer_pad)
            return Gst.PadProbeReturn.DROP

        return Gst.PadProbeReturn.OK

    def elements_changestate(self):
        """Change state to playing."""
        self.VideoTemplateBin.set_state(Gst.State.PLAYING)
        self.AudioTemplateBin.set_state(Gst.State.PLAYING)
