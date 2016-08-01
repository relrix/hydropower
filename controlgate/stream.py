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
from threading import Thread
import gi
import time
gi.require_version('Gst', '1.0')
GObject.threads_init()
Gst.init(None)


class avbin():
    """audio video bin."""

    def __init__(self, pipeline, videomix, videoMixer_pad, audiomix, audioMixer_pad, rtmp_location):
        """init."""
        self.pipeline = pipeline
        self.videomix = videomix
        self.videoMixer_pad = videoMixer_pad
        self.audioMixer_pad = audioMixer_pad
        self.rtmp_location = rtmp_location
        self.audiomix = audiomix
        self.CustomBin = Gst.Bin.new(None)
        self.decodercustomBin = Gst.Bin.new(None)

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
        self.videosrc.set_property("blocksize", 512)

        self.decodebin.set_property("message-forward", "true")
        self.decodebin.connect('pad-added', self.on_pad_added)
        self.videoscale.set_property("method", "bilinear")
        self.videocaps.set_property("caps", Gst.Caps.from_string("video/x-raw,framerate=30/1,format=I420,width=146,height=90"))

        """add elements to CustomBin."""

        for element in (self.decodevidqueue, self.videoscale, self.videorate, self.videocaps, self.videoconvert, self.videosinkqueue):
            self.CustomBin.add(element)

        self.decodercustomBin.add(self.videosrc)
        self.decodercustomBin.add(self.decodebin)
        """link elements to CustomBin."""

        self.videosrc.link(self.decodebin)
        self.decodebin.link(self.decodevidqueue)

        self.decodevidqueue.link(self.videoscale)
        self.videoscale.link(self.videorate)
        self.videorate.link(self.videocaps)
        self.videocaps.link(self.videoconvert)
        self.videoconvert.link(self.videosinkqueue)

        Connectpad = self.videosinkqueue.get_static_pad("src")
        self.ghostPad = Gst.GhostPad.new(None, Connectpad)
        self.CustomBin.add_pad(self.ghostPad)
        ConnectpadSink = self.decodevidqueue.get_static_pad('sink')
        self.ghostPad1 = Gst.GhostPad.new(None, ConnectpadSink)
        self.CustomBin.add_pad(self.ghostPad1)

        self.audiobin, self.audqueuesink, self.audqueuesrc, self.audioelement = get_bin_pad(self.pipeline, self.decodebin)
        # self.decodebin.link(self.audiobin)
        self.pipeline.add(self.decodercustomBin)
        self.pipeline.add(self.CustomBin)

        clock = self.pipeline.get_clock()
        self.CustomBin.set_base_time(self.pipeline.get_base_time())
        self.CustomBin.set_clock(clock)
        self.decodercustomBin.set_base_time(self.pipeline.get_base_time())
        self.decodercustomBin.set_clock(clock)

        # if not self.tile:
        # self.CustomBin.set_state(Gst.State.READY)
        # self.decodercustomBin.set_state(Gst.State.READY)
        # self.audiobin.set_state(Gst.State.READY)
        self.CustomBin.set_state(Gst.State.PLAYING)
        self.decodercustomBin.set_state(Gst.State.PLAYING)
        self.audiobin.set_state(Gst.State.PLAYING)

        # if self.tile:
        self.ghostPad1.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.cb_event, None)

        self.ghostPad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.eos_event, None)

        return self.CustomBin, self.ghostPad, self.ghostPad1, self.audqueuesrc, self.audioelement, self.videocaps

    def eos_event(self, pad, info, user_data):
        """on EOS EVENT."""
        EventType = info.get_event().type
        print str(EventType) + " _____VIDEO_____"
        if(EventType == Gst.EventType.EOS):
            print("End-Of-Stream reached. VIDEO")
            releaseThread = Thread(target=self.release_resources, args=())
            releaseThread.start()

            return Gst.PadProbeReturn.DROP

        return Gst.PadProbeReturn.OK

    def release_resources(self):
        self.CustomBin.set_state(Gst.State.NULL)
        self.decodercustomBin.set_state(Gst.State.NULL)
        self.audiobin.set_state(Gst.State.NULL)
        self.pipeline.remove(self.CustomBin)
        self.pipeline.remove(self.decodercustomBin)
        self.pipeline.remove(self.audiobin)
        # TODO do clean ups for later
        print("RELEASE REQUEST FOR AUDIO VIDEO PADS")
        self.videomix.release_request_pad(self.videoMixer_pad)
        self.audiomix.release_request_pad(self.audioMixer_pad)

    def on_pad_added(self, element, pad):
        """Callback to link a/v sink to decoder source."""
        string = pad.query_caps(None).to_string()

        if string.startswith('video/'):
            ghostPad = Gst.GhostPad.new(None, pad)
            ghostPad.set_active(True)
            self.decodercustomBin.add_pad(ghostPad)
            ghostPad.link(self.ghostPad1)

        elif string.startswith('audio/'):
            print "linking audio with decoder"
            ghostPad = Gst.GhostPad.new(None, pad)
            ghostPad.set_active(True)
            self.decodercustomBin.add_pad(ghostPad)
            state = ghostPad.link(self.audqueuesink)
            print state

            # if self.tile:
            # audqueuesrc.link(self.flvmuxer.get_request_pad())

    def elements_changestate(self):
        """Change state to playing."""
        self.CustomBin.set_state(Gst.State.PLAYING)

    def cb_event(self, pad, info, user_data):
        """call back event."""
        EventType = info.get_event().type
        if(EventType == Gst.EventType.SEGMENT):

            newSegment = Gst.Segment.new()
            newSegment.init(Gst.Format.TIME)
            newSegment.rate = 1.0
            newSegment.format = 3
            clock = Gst.SystemClock.obtain()
            newSegment.offset_running_time(Gst.Format.TIME, clock.get_time() - self.pipeline.get_base_time())
            # newSegment.to_position(Gst.Format.TIME,clock.get_time() - self.pipeline.get_base_time())
            videoscale = self.videoscale.get_static_pad("sink")
            videoscale.send_event(Gst.Event.new_segment(newSegment))

            print "On Video Segment "
            return Gst.PadProbeReturn.DROP

        elif(info.get_event().has_name("custom_videocaps")):
            print "Got my custom message"
            custom_structure = info.get_event().get_structure()
            videocaps = custom_structure.get_string("data")
            print videocaps
            print "i have a caps of " + custom_structure.get_string("data")

            self.videocaps.get_static_pad('sink').add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.caps_cb, custom_structure)
            # custom_structure.free()
            return Gst.PadProbeReturn.DROP
            # segment = info.get_event().parse_segment();
            # print("SEGMENT Rate = %f StartTime = %d StopTime = %d Time = %d Base= %d duration %d format %d " % (segment.rate,segment.start,segment.stop,segment.time,segment.base,segment.duration,segment.format))
            # clock = Gst.SystemClock.obtain()
            # state = segment.offset_running_time(Gst.Format.TIME, clock.get_time() - self.pipeline.get_base_time())
            # print "VIDEO RUNNING TIME STATE " + str (state)
        return Gst.PadProbeReturn.OK

    def caps_cb_test(self, pad, info, caps):
        """test callback."""
        pad.remove_probe(info.id)
        print " I am in caps_cb_test"
        self.videocaps.get_static_pad('sink').add_probe(Gst.PadProbeType.BLOCK | Gst.PadProbeType.EVENT_DOWNSTREAM, self.caps_cb, caps)
        # self.videoscale.get_static_pad('sink').send_event(Gst.Event.new_eos())
        return Gst.PadProbeReturn.OK

    def catch_flush(self, pad, info, custom_structure):
        """flush cacahe."""
        videocaps = custom_structure.get_string("data")
        maincap = custom_structure.get_value("on24cap")
        speaker_past = custom_structure.get_string("past_speaker")

        EventType = info.get_event().type
        # pad.remove_probe(info.id)
        print str(EventType) + " _____VIDEO_____CATCH FLUSH__"

        if(EventType == Gst.EventType.FLUSH_START):
            print ("GOT FLUSH START")
            return Gst.PadProbeReturn.DROP
        elif(EventType == Gst.EventType.FLUSH_STOP):
            print ("GOT FLUSH STOP")
            pad.remove_probe(info.id)
            temp_xpos = self.videoMixer_pad.get_property("xpos")
            temp_ypos = self.videoMixer_pad.get_property("ypos")
            temp_zorder = self.videoMixer_pad.get_property("zorder")
            self.videoMixer_pad.set_property("xpos", 0)
            self.videoMixer_pad.set_property("ypos", 0)
            self.videoMixer_pad.set_property("zorder", 2)

            if maincap is not None:
                maincap.set_property("caps", Gst.Caps.from_string("video/x-raw,framerate=30/1,format=I420,width=146,height=90"))
                self.videomix.get_static_pad(speaker_past).set_property("xpos", temp_xpos)
                self.videomix.get_static_pad(speaker_past).set_property("ypos", temp_ypos)
                self.videomix.get_static_pad(speaker_past).set_property("zorder", temp_zorder)

            # run = True
            # zorder = 2
            # vid_sink_pads_ite = self.videomix.iterate_sink_pads()
            # while(run):
            #     ret, pads = vid_sink_pads_ite.next()
            #     if ret == Gst.IteratorResult.OK:
            #         print "Zorder ", pads.get_name(), pads.get_property("zorder")
            #         if "sink_0" not in pads.get_name():
            #             if(pads.get_name() in self.videoMixer_pad.get_name()):
            #                 pass
            #             else:
            #                 pads.set_property("zorder", zorder)
            #                 zorder = zorder + 1
            #
            #     if ret != Gst.IteratorResult.OK:
            #         print "Breaking Iterator"
            #         run = False
            #         break
            # run = True
            # while(run):
            #     ret, pads = vid_sink_pads_ite.next()
            #     if ret == Gst.IteratorResult.OK:
            #         print "Zorder AFTER ", pads.get_name(), pads.get_property("zorder")
            #     if ret != Gst.IteratorResult.OK:
            #         print "Breaking Iterator"
            #         run = False
            #         break


            # if self.videoMixer_pad.get_name() == "sink_1":
            #     self.videomix.get_static_pad("sink_2").set_property("xpos", 0)
            #     self.videomix.get_static_pad("sink_2").set_property("ypos", 0)
            #     self.videomix.get_static_pad("sink_2").set_property("zorder", 1)
            # else:
            #     self.videomix.get_static_pad("sink_1").set_property("xpos", 0)
            #     self.videomix.get_static_pad("sink_1").set_property("ypos", 0)
            #     self.videomix.get_static_pad("sink_1").set_property("zorder", 1)

            #else:
            #    self.videoMixer_pad.set_property("xpos", 480)
            #    self.videoMixer_pad.set_property("ypos", 20)
            #    self.videoMixer_pad.set_property("zorder", 2)
            return Gst.PadProbeReturn.DROP

        return Gst.PadProbeReturn.DROP

    def caps_cb(self, pad, info, custom_structure):
        """caps callback on probe."""
        videocaps = custom_structure.get_string("data")
        maincap = custom_structure.get_value("on24cap")
        speaker_past = custom_structure.get_string("past_speaker")
        # self.CustomBin.set_state(Gst.State.PAUSED)
        # self.decodercustomBin.set_state(Gst.State.PAUSED)
        # self.audiobin.set_state(Gst.State.PAUSED)
        # self.CustomBin.set_state(Gst.State.PLAYING)
        # self.decodercustomBin.set_state(Gst.State.PLAYING)
        # self.audiobin.set_state(Gst.State.PLAYING)
        # if(self.videoMixer_pad.get_name() == "sink_0"):
        #if maincap is not None:
            #self.videomix.get_static_pad(speaker_past).set_property("zorder", 0)

        pad.get_parent_element().set_property("caps", Gst.Caps.from_string(videocaps))
        if speaker_past is not None:
            self.videomix.get_static_pad(speaker_past).set_property("zorder", 0)

        print "We got cap as ", maincap
        pad.remove_probe(info.id)
        self.videosinkqueue.get_static_pad("sink").add_probe(Gst.PadProbeType.BLOCK | Gst.PadProbeType.EVENT_DOWNSTREAM | Gst.PadProbeType.EVENT_FLUSH, self.catch_flush, custom_structure)
        self.videocaps.get_static_pad("sink").send_event(Gst.Event.new_flush_start())
        # self.videosinkqueue.get_static_pad("sink").add_probe(Gst.PadProbeType.BLOCK | Gst.PadProbeType.EVENT_DOWNSTREAM | Gst.PadProbeType.EVENT_FLUSH, self.catch_flush, videocaps)
        self.videocaps.get_static_pad("sink").send_event(Gst.Event.new_flush_stop(True))

        return Gst.PadProbeReturn.DROP
        # if(custom_structure.get_value("width") == 640):
        #     self.videoMixer_pad.set_property("xpos", 0)
        #     self.videoMixer_pad.set_property("ypos", 0)
        #     self.videoMixer_pad.set_property("zorder",0)
        # else:
        #     self.videoMixer_pad.set_property("xpos", 480)
        #     self.videoMixer_pad.set_property("ypos", 20)
        #     self.videoMixer_pad.set_property("zorder",1)
        # ##self.videocaps.get_static_pad('src').send_event(Gst.Event.new_flush_start())
        # #self.videocaps.get_static_pad('src').send_event(Gst.Event.new_flush_stop(True))
        #
        # return Gst.PadProbeReturn.DROP
        #
        # if(info.get_event().type != Gst.EventType.FLUSH_START and info.get_event().type != Gst.EventType.FLUSH_STOP):
        #     return Gst.PadProbeReturn.PASS
        # #if info.get_event().type !=  Gst.EventType.EOS:
        # #    return Gst.PadProbeReturn.PASS
        # # if(caps != None):
        #
        # if(info.get_event().type == Gst.EventType.FLUSH_START):
        #     print ("GOT FLUSH START HERE ____")
        #     return Gst.PadProbeReturn.DROP
        # elif(info.get_event().type == Gst.EventType.FLUSH_STOP):
        #     pad.remove_probe(info.id)
        #     #pad.get_parent_element().set_state(Gst.State.NULL)
        #     print " my current cap is " + str(pad.get_current_caps())
        #     print " I have chil of "+ pad.get_parent_element().get_name()
        #     pad.get_parent_element().set_property("caps", Gst.Caps.from_string(caps))
        #     return Gst.PadProbeReturn.DROP
        # #pad.mark_reconfigure()
        # #self.CustomBin.remove(self.videocaps)
        # #self.videocaps.set_property("caps", Gst.Caps.from_string(caps))
        #     #pad.get_parent_element().set_state(Gst.State.PLAYING)
        # #self.videorate.link(self.videocaps)
        # #self.videocaps.link(self.videoconvert)
        #
        # return Gst.PadProbeReturn.PASS

    def buff_event(self, pad, info, user_data):
        """block start segment."""
        # buf = info.get_buffer()
        # print("before BUFF PTS = %f  DTS %f duration %f " %(buf.pts,buf.dts,buf.duration))
        # clock = Gst.SystemClock.obtain()
        # buf.pts = clock.get_time() - self.pipeline.get_base_time() + buf.duration
        # buf.dts = clock.get_time() - self.pipeline.get_base_time() - buf.duration
        # print("after BUFF PTS = %f  DTS %f duration %f " %(buf.pts,buf.dts,buf.duration))
        return Gst.PadProbeReturn.OK


# def get_video_caps(tile=True):
#     """get vidoe caps."""
#     if not tile:
#         return "video/x-raw,framerate=30/1,format=I420,width=640,height=360"
#     else:
#         return "video/x-raw,framerate=30/1,format=I420,width=146,height=90"


def get_stream_for_mix(pipeline=None, videomix=None, videoMixer_pad=None, audiomix=None, audioMixer_pad=None, rtmpsrc=None):
    """Get required param to create a bin."""
    if not rtmpsrc or not pipeline or not videoMixer_pad or not audiomix:
        raise Exception('Mandotarty fields are missing')
    bin = avbin(pipeline, videomix, videoMixer_pad, audiomix, audioMixer_pad, rtmpsrc)
    custom_bin, pad, vidsinkpad, audqueuesrc, audioelement, vidcaps = bin.get_ghost_pad()
    return custom_bin, pad, vidsinkpad, audqueuesrc, audioelement, vidcaps
