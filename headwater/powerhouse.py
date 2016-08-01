"""Powerhouse class.

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

import gi
import sys
import controlgate.basestream as templateStream
from impoundment import impoundment
from threading import Thread
from controlgate import stream
from gi.repository import GObject
from gi.repository import Gst
gi.require_version('Gst', '1.0')
# GLib is used for timeout testing
# from gi.repository import GLib

GObject.threads_init()
Gst.init(None)

Gst.debug_set_active(True)
Gst.debug_set_default_threshold(3)
# Gst.debug_set_threshold_for_name("videomixer", 6)
# Gst.debug_set_threshold_for_name("audiomixer", 9)
# Gst.debug_set_threshold_for_name("rtmpsrc", 9)


class powerhouse(Thread):
    """Powerhouse class."""

    def __init__(self, dsturl):
        """initialize variables."""
        Thread.__init__(self)
        self.rtmpdst = dsturl
        self.pipeline = Gst.Pipeline()
        self.bus = self.pipeline.get_bus()
        self.main_loop = GObject.MainLoop(None)
        self.bus.add_signal_watch()
        self.bus.connect("message", self.cb_message, None)
        # self.bus.connect("sync-message::element",self.on_sync_msg,None)
        self.streams = {}
        self.streams["sink_0"] = {}
        self.sink_count = 1
        self.impoundmentObj = impoundment()

        # TEST ONE
        self.which_main = "sink_1"

    def run(self):
        """Element to drain out the stream to rtmpsink."""
        self.videomix = Gst.ElementFactory.make("videomixer", "videomixer")
        self.audiomix = Gst.ElementFactory.make("audiomixer", "audiomixer")
        self.aacencode = Gst.ElementFactory.make("avenc_aac", "audioencoder")
        self.x264enc = Gst.ElementFactory.make("x264enc", "videoencoder")
        self.flvmux = Gst.ElementFactory.make("flvmux", "rtmpmuxer")
        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", "rtmpsink")
        # self.videomix = Gst.ElementFactory.make("compositor", None)

        self.videomix.connect('pad-added', self.on_pad_added_video)
        self.videomix.connect('pad-removed', self.on_pad_removed_video)

        self.videomix.set_property("background", "black")
        # self.audiomix.connect('pad-added', self.on_pad_added_audio)
        # self.audiomix.connect('pad-removed', self.on_pad_removed_audio)

        self.aacencode.set_property("compliance", -2)
        # self.aacencode.set_property("bitrate",64000)
        # self.aacencode.set_property("perfect-timestamp",True)
        # self.aacencode.set_property("hard-resync",True)

        self.x264enc.set_property("byte-stream", True)
        self.x264enc.set_property("pass", "qual")
        self.x264enc.set_property("b-adapt", False)
        self.x264enc.set_property("speed-preset", "ultrafast")
        self.x264enc.set_property("key-int-max", 75)

        self.flvmux.set_property("streamable", True)
<<<<<<< HEAD
        # self.flvmux.connect('pad-added', self.on_pad_added_muxer)
        # gself.rtmpsink.set_property("location", "rtmp://172.18.5.221/onestream/shishir")
        self.rtmpsink.set_property("location", self.rtmpdst)
=======
        #self.flvmux.connect('pad-added', self.on_pad_added_muxer)
        self.rtmpsink.set_property("location", "rtmp://172.18.5.221/onestream/shishir")
>>>>>>> dce5e2c60e5de5f2a7bf4a5e9f7984c60a169d86

        self.pipeline.add(self.videomix)
        self.pipeline.add(self.audiomix)
        self.pipeline.add(self.aacencode)
        self.pipeline.add(self.x264enc)
        self.pipeline.add(self.flvmux)
        self.pipeline.add(self.rtmpsink)

        self.videomix.link(self.x264enc)
        self.audiomix.link(self.aacencode)
        self.aacencode.link(self.flvmux)
        self.x264enc.link(self.flvmux)
        self.flvmux.link(self.rtmpsink)

        # temppad = self.videomix.get_static_pad("src")
        # temppad.add_probe(Gst.PadProbeType.EVENT_BOTH, self.block_event, None)
        # GLib.timeout_add_seconds(20, self.timeout_cb, None)

        # def block_event(self, pad, info, userdata):
        #     EventType = info.get_event().type
        #     print "Videomix event Type => " + str(EventType)
        #    return Gst.PadProbeReturn.OK
        #
        # def timeout_cb(self, userdata):
        #     """sometimeout."""
        #     print "NOW ADDING"
        #     self.add_streams("rtmp://192.168.0.1/stream/newstream live=1", False)
        #     return True
        # self.add_streams("rtmp://qa-fmslivea.on24.com/livestreama/1289386_1_fhvideo1_43454BEF7173A33865889E60F49CDADC live=1", True)
        self.InitiliazeBaseStream()

    def InitiliazeBaseStream(self):
        videomix_pad = self.videomix.get_request_pad("sink_0")
        audiomix_pad = self.audiomix.get_request_pad("sink_0")
        templateholder = templateStream.avbin(self.pipeline, videomix_pad, audiomix_pad)
        # returns self.VideoTemplateBin, self.AudioTemplateBin, ghostPad, ghostPad1
        self.streams["sink_0"]["videobin"], self.streams["sink_0"]["audiobin"], self.streams["sink_0"]["vidqsrcpad"], self.streams["sink_0"]["audioqsrcpad"] = templateholder.get_connect_pads()
        self.streams["sink_0"]["vidqsrcpad"].link(videomix_pad)
        self.streams["sink_0"]["audioqsrcpad"].link(audiomix_pad)
        self.start_genetrator()


    def start_genetrator(self):
        """start the pipeline."""
        clock = Gst.SystemClock.obtain()
        self.pipeline.set_base_time(clock.get_time())
        self.pipeline.set_state(Gst.State.PLAYING)
        self.main_loop.run()

    def add_streams(self, rtmpsrc):
        """create dictionary of created Objects."""
        # if mainWindow:
        self.streams["sink_" + str(self.sink_count)] = {}
        videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
        audiomix_pad = self.audiomix.get_request_pad("sink_" + str(self.sink_count))
        audiomix_pad.set_active(True)
        videomix_pad.set_active(True)
        # self.pipeline.add(self.streams["sink_" + str(self.sink_count)]["bin"])
        self.streams["sink_" + str(self.sink_count)]["pad"].link(videomix_pad)
        self.streams["sink_" + str(self.sink_count)]["audioqsrcpad"].link(audiomix_pad)
        # videomix_pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.bin_probe_event_cb, None)
        self.sink_count = self.sink_count + 1
        # self.start_genetrator()
        # else:
        #    self.addVideoTiles(rtmpsrc)
        #    return

    # def on_pad_added_muxer(self, element, pad):
    #     """call back to linke audio."""
    #     string = pad.query_caps(None).to_string()
    #     print pad.get_name()
    #
    #     if string.startswith('audio/'):
    #         print "Adding audio muxer"
            # self.streams["sink_0"]["audioqsrcpad"].link(pad)

    def stop(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.main_loop.quit()

    def on_pad_removed_video(self, element, pad):
        """pad removed."""
        self.sink_count = self.sink_count - 1
        print "video pad removed"

    def on_pad_added_video(self, element, pad):
        """Callback to link a/v sink to decoder source."""
        # if(pad.get_name() == "sink_0"):
        #    return
        sink = self.impoundmentObj.get_sink_location(pad.get_name(), 404)
        print sink
        pad.set_property("xpos", sink["xpos"])
        pad.set_property("ypos", sink["ypos"])
        pad.set_property("zorder", sink["zorder"])

    def addVideoTiles(self, rtmpsrc, presenter_id):
        """stopStream and add new video Tiles."""
        # self.streams["sink_0"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.sink_probe_event_cb, rtmpsrc)
        t = Thread(target=self.sink_probe_event_cb, args=(rtmpsrc, presenter_id,))
        t.start()
        # self.streams["sink_" + str(self.sink_count)] = {}
        # videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
        # self.streams["sink_" + str(self.sink_count)]["bin"], self.streams["sink_" + str(self.sink_count)]["pad"] = stream.get_stream_for_mix(pipeline=self.pipeline, mixer_pad=videomix_pad, rtmpsrc=rtmpsrc, tile=True)
        # videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
        # self.pipeline.add(self.streams["sink_" + str(self.sink_count)]["bin"])
        # self.streams["sink_" + str(self.sink_count)]["pad"].link(videomix_pad)
        # videomix_pad.set_active(True)
        # videomix_pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.bin_probe_event_cb, None)
        # self.sink_count = self.sink_count + 1

    # def bin_probe_event_cb(self, pad, info, user_data):
    #     """add probing for custon bin."""
    #     EventType = info.get_event().type
    #
    #     if(EventType == Gst.EventType.EOS):
    #         pad.remove_probe(info.id)
    #         pad.set_active(False)
    #         self.streams[pad.get_name()]["bin"].set_state(Gst.State.NULL)
    #         self.streams[pad.get_name()]["pad"].unlink(pad)
    #         self.videomix.release_request_pad(pad)
    #
    #     return Gst.PadProbeReturn.OK

    def sink_probe_event_cb(self, user_data, presenter_id):
        """probe."""
        self.streams["sink_" + str(self.sink_count)] = {}
        videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
        audiomix_pad = self.audiomix.get_request_pad("sink_" + str(self.sink_count))
        audiomix_pad.set_active(True)
        videomix_pad.set_active(True)
        self.streams["sink_" + str(self.sink_count)]["bin"], self.streams["sink_" + str(self.sink_count)]["pad"], self.streams["sink_" + str(self.sink_count)]["vidsinkpad"], self.streams["sink_" + str(self.sink_count)]["audioqsrcpad"], self.streams["sink_" + str(self.sink_count)]["audioqueue"], self.streams["sink_" + str(self.sink_count)]["vidcaps"] = stream.get_stream_for_mix(pipeline=self.pipeline, videomix=self.videomix, videoMixer_pad=videomix_pad, audiomix=self.audiomix, audioMixer_pad=audiomix_pad, rtmpsrc=user_data)
        # self.pipeline.add(self.streams["sink_" + str(self.sink_count)]["bin"])
        self.streams["sink_" + str(self.sink_count)]["pad"].link(videomix_pad)
        self.streams["sink_" + str(self.sink_count)]["audioqsrcpad"].link(audiomix_pad)
        # self.streams["sink_" + str(self.sink_count)]["bin"].set_state(Gst.State.PLAYING)
        # videomix_pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.bin_probe_event_cb, None)
        self.impoundmentObj.set_sink("sink_" + str(self.sink_count), presenter_id)
        self.sink_count = self.sink_count + 1

    def changeStream(self, presenter_id):
        """change stream."""

        vid_sink_pads_ite = self.videomix.iterate_sink_pads()
        run = True
        speaker_past = None
        speaker_now = None
        while(run):
            ret, pads = vid_sink_pads_ite.next()
            if ret == Gst.IteratorResult.OK:
                if(pads.get_property("xpos") == 0 and "sink_0" not in pads.get_name()):
                    speaker_past = pads.get_name()
                    #pads.set_property("zorder", 0)
                    run = False
                    break
            if ret != Gst.IteratorResult.OK:
                print "Breaking Iterator"
                run = False
                break

        keypaths = self.impoundmentObj.get_all_sinks()
        for key, value in keypaths.iteritems():
            print value
            for subkey, subvalue in value.iteritems():
                if presenter_id == subvalue:
                    speaker_now = key
                    break

        print "Speaker past ", speaker_past
        print "Speaker now ", speaker_now

        if speaker_past is not None:
            if(speaker_now in speaker_past):
                print "You are already a speaker"
                return

        gst_structure_main = Gst.Structure.new_empty("custom_videocaps")
        gst_structure_main.set_value("data", "video/x-raw,framerate=30/1,format=I420,width=640,height=360")

        gst_structure_tile = Gst.Structure.new_empty("custom_videocaps")
        gst_structure_tile.set_value("data", "video/x-raw,framerate=30/1,format=I420,width=146,height=90")

        # self.custom_message_main = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_main)
        # self.custom_message_tile = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_tile)

        # self.streams["sink_1"]["vidsinkpad"].send_event(Gst.Event.new_flush_start())
        # self.streams["sink_1"]["vidsinkpad"].send_event(Gst.Event.new_flush_stop(True))
        # self.streams["sink_0"]["vidsinkpad"].send_event(Gst.Event.new_flush_start())
        # self.streams["sink_0"]["vidsinkpad"].send_event(Gst.Event.new_flush_stop(True))

        if speaker_past is None:
            gst_structure_tile.set_value("on24cap", "")
            gst_structure_tile.set_value("past_speaker", "")
            self.gst_structure_main = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_main)
            self.streams[speaker_now]["vidsinkpad"].send_event(self.gst_structure_main)
        else:
            gst_structure_main.set_value("on24cap", self.streams[speaker_past]["vidcaps"])
            gst_structure_main.set_value("past_speaker", speaker_past)
            self.custom_message_main = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_main)
            self.streams[speaker_now]["vidsinkpad"].send_event(self.custom_message_main)

            # gst_structure_tile.set_value("on24cap", self.streams[speaker_now]["vidcaps"])
            #gst_structure_tile.set_value("now_speaker", speaker_now)
            #self.custom_message_tile = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_tile)
            #self.streams[speaker_past]["vidsinkpad"].send_event(self.custom_message_tile)

        # if self.which_main == "sink_1":
        #     self.which_main = "sink_2"
        #     # send_main = {"mainpad":"sink_1","tilepad":"sink_0"}
        #     # send_tile = {"pad":"sink_0","mode":"tile"}
        #     gst_structure_tile.set_value("on24cap", self.streams["sink_2"]["vidcaps"])
        #     self.custom_message_tile = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_tile)
        #     self.streams["sink_1"]["vidsinkpad"].send_event(self.custom_message_tile)
            # self.streams["sink_2"]["vidsinkpad"].send_event(self.custom_message_main)
            # self.streams["sink_0"]["pad"].add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM|Gst.PadProbeType.EVENT_FLUSH, self.change_sink_cb, send_main)
            # self.streams["sink_1"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM | Gst.PadProbeType.EVENT_DOWNSTREAM | Gst.PadProbeType.EVENT_FLUSH, self.change_sink_cb1, send_main)
            # self.streams["sink_0"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM | Gst.PadProbeType.EVENT_DOWNSTREAM | Gst.PadProbeType.EVENT_FLUSH, self.change_sink_cb, send_tile)
            # self.streams["sink_1"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.change_sink_cb1, send_main)
            # self.streams["sink_0"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.change_sink_cb, send_main)
        # elif self.which_main == "sink_2":
        #     self.which_main = "sink_1"
        #     # send_main = {"mainpad":"sink_0","tilepad":"sink_1"}
        #     gst_structure_tile.set_value("on24cap", self.streams["sink_1"]["vidcaps"])
        #     self.custom_message_tile = Gst.Event.new_custom(Gst.EventType.CUSTOM_DOWNSTREAM, gst_structure_tile)
        #
        #     self.streams["sink_2"]["vidsinkpad"].send_event(self.custom_message_tile)
            # self.streams["sink_1"]["vidsinkpad"].send_event(self.custom_message_main)
            # self.streams["sink_0"]["pad"].add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM|Gst.PadProbeType.EVENT_FLUSH, self.change_sink_cb, send_main)
            # send_main = {"mainpad":"sink_0","tilepad":"sink_1"}
            # send_tile = {"pad":"sink_1","mode":"tile"}
            # self.streams["sink_1"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.change_sink_cb, send_tile)

        # return Gst.PadProbeReturn.DROP

    def cb_message(self, bus, msg, data):
        """callback to catch messages flowing on the powerhouse."""
        if (msg.type == Gst.MessageType.ERROR):
            err, debug = msg.parse_error()
            print >> sys.stderr, ("Error: {0}".format(err.message))
            self.pipeline.set_state(Gst.State.READY)
            self.main_loop.quit()
            sys.exit(0)

        elif (msg.type == Gst.MessageType.EOS):
            print("End-Of-Stream reached.")

        elif (msg.type == Gst.MessageType.BUFFERING):
            percent = msg.parse_buffering()
            sys.stdout.write("\rBuffering ({0}%)".format(percent))
            sys.stdout.flush()
            if (percent < 0):
                self.pipeline.set_state(Gst.State.PAUSED)
            else:
                self.pipeline.set_state(Gst.State.PLAYING)

        elif (msg.type == Gst.MessageType.CLOCK_LOST):
            print "CLOCK LOST"
            self.pipeline.set_state(Gst.State.PAUSED)
            self.pipeline.set_state(Gst.State.PLAYING)
        else:
            pass
