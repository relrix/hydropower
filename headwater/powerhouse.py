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
#Gst.debug_set_threshold_for_name("videomixer", 6)
# Gst.debug_set_threshold_for_name("rtmpsrc", 9)


class powerhouse():
    """Powerhouse class."""

    def __init__(self):
        """initialize variables."""
        self.pipeline = Gst.Pipeline()
        self.bus = self.pipeline.get_bus()
        self.main_loop = GObject.MainLoop(None)
        self.bus.add_signal_watch()
        self.bus.connect("message", self.cb_message, None)
        # self.bus.connect("sync-message::element",self.on_sync_msg,None)
        self.streams = {}
        self.streams["sink_0"] = {}
        self.sink_count = 0
        self.impoundmentObj = impoundment()

    def tailrace(self):
        """Element to drain out the stream to rtmpsink."""
        self.videomix = Gst.ElementFactory.make("videomixer", None)
        # self.videomix = Gst.ElementFactory.make("compositor", None)
        self.videomix.connect('pad-added', self.on_pad_added)
        self.videomix.connect('pad-removed', self.on_pad_removed)
        self.pipeline.add(self.videomix)

        self.x264enc = Gst.ElementFactory.make("x264enc", None)
        self.x264enc.set_property("byte-stream", True)
        self.x264enc.set_property("pass", "qual")
        self.x264enc.set_property("b-adapt", False)
        self.x264enc.set_property("speed-preset", "veryfast")
        self.x264enc.set_property("key-int-max", 75)
        self.pipeline.add(self.x264enc)

        self.flvmux = Gst.ElementFactory.make("flvmux", None)
        self.flvmux.set_property("streamable", True)
        self.flvmux.connect('pad-added', self.on_pad_added_muxer)
        self.pipeline.add(self.flvmux)

        self.rtmpsink = Gst.ElementFactory.make("rtmpsink", None)
        self.rtmpsink.set_property("location", "rtmp://172.18.5.221/onestream/shishir")

        self.pipeline.add(self.rtmpsink)
        self.videomix.link(self.x264enc)
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

    def start_genetrator(self):
        """start the pipeline."""
        clock = Gst.SystemClock.obtain()
        self.pipeline.set_base_time(clock.get_time())
        self.pipeline.set_state(Gst.State.PLAYING)
        self.main_loop.run()

    def add_streams(self, rtmpsrc, mainWindow):
        """create dictionary of created Objects."""
        if mainWindow:
            videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
            self.streams["sink_" + str(self.sink_count)]["bin"], self.streams["sink_" + str(self.sink_count)]["pad"], self.streams["sink_" + str(self.sink_count)]["audioqsrcpad"], self.streams["sink_" + str(self.sink_count)]["audioqueue"] = stream.get_stream_for_mix(pipeline=self.pipeline, mixer_pad=videomix_pad, rtmpsrc=rtmpsrc, flvmuxer=self.flvmux, tile=False)
            #self.pipeline.add(self.streams["sink_" + str(self.sink_count)]["bin"])
            self.streams["sink_" + str(self.sink_count)]["pad"].link(videomix_pad)
            tempPad = self.flvmux.get_request_pad("audio")
            state = self.streams["sink_0"]["audioqsrcpad"].link(tempPad)
            print "Flv pad link state " + str (state)
            #videomix_pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.bin_probe_event_cb, None)
            self.sink_count = self.sink_count + 1
            self.start_genetrator()
        else:
            self.addVideoTiles(rtmpsrc)
            return

    def on_pad_added_muxer(self, element, pad):
        """call back to linke audio."""
        string = pad.query_caps(None).to_string()
        print pad.get_name()

        if string.startswith('audio/'):
            print "Adding audio muxer"
            #self.streams["sink_0"]["audioqsrcpad"].link(pad)

    def on_pad_removed(self, element, pad):
        """pad removed."""
        self.sink_count = self.sink_count - 1
        print "padremoved"

    def on_pad_added(self, element, pad):
        """Callback to link a/v sink to decoder source."""
        if(pad.get_name() == "sink_0"):
            return
        sink = self.impoundmentObj.get_sink_location(pad.get_name())
        pad.set_property("xpos", sink["xpos"])
        pad.set_property("ypos", sink["ypos"])

    def addVideoTiles(self, rtmpsrc):
        """stopStream and add new video Tiles."""
        # self.streams["sink_0"]["pad"].add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.sink_probe_event_cb, rtmpsrc)
        t = Thread(target=self.sink_probe_event_cb, args=(rtmpsrc,))
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

    def bin_probe_event_cb(self, pad, info, user_data):
        """add probing for custon bin."""
        EventType = info.get_event().type

        if(EventType == Gst.EventType.EOS):
            pad.remove_probe(info.id)
            pad.set_active(False)
            self.streams[pad.get_name()]["bin"].set_state(Gst.State.NULL)
            self.streams[pad.get_name()]["pad"].unlink(pad)
            self.videomix.release_request_pad(pad)

        return Gst.PadProbeReturn.OK

    def sink_probe_event_cb(self, user_data):
        """probe."""
        self.streams["sink_" + str(self.sink_count)] = {}
        videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
        self.streams["sink_" + str(self.sink_count)]["bin"], self.streams["sink_" + str(self.sink_count)]["pad"], self.streams["sink_" + str(self.sink_count)]["audioqsrcpad"], self.streams["sink_" + str(self.sink_count)]["audioqueue"] = stream.get_stream_for_mix(pipeline=self.pipeline, mixerelement = self.videomix, mixer_pad=videomix_pad, rtmpsrc=user_data, flvmuxer=self.flvmux, tile=True)
        # self.pipeline.add(self.streams["sink_" + str(self.sink_count)]["bin"])
        self.streams["sink_" + str(self.sink_count)]["pad"].link(videomix_pad)
        videomix_pad.set_active(True)
        self.streams["sink_" + str(self.sink_count)]["bin"].set_state(Gst.State.PLAYING)
        #videomix_pad.add_probe(Gst.PadProbeType.EVENT_DOWNSTREAM, self.bin_probe_event_cb, None)
        self.sink_count = self.sink_count + 1
    #
    #     print "BLOCKING ENds"
    #
    # def stream_probe_cb(self, pad, info, user_data):
    #     """stream probe callback."""
    #     print "I am blocked"
    #     pad.remove_probe(info.id)
    #     if not self.videomix.get_static_pad('src').is_blocking() and not self.videomix.get_static_pad('src').is_blocked():
    #         print "BLOCK STREAM"
    #
    #     while(True):
    #         ret, val = gstiterator.next()
    #         if ret == Gst.IteratorResult.OK:
    #             print val.get_name()
    #         if ret != Gst.IteratorResult.OK:
    #             print "Error"
    #         if ret == Gst.IteratorResult.OK:
    #             break
    #
    #         if not self.eos_send:
    #             self.eos_send = True
    #             videomix_pad = self.videomix.get_request_pad("sink_" + str(self.sink_count))
    #             self.streams["tileWindow"+str(self.sink_count)] = turbine.turbine(pipeline=self.pipeline, rtmp_location=user_data, videocap=self.tileWindow_cap, mix_sink=videomix_pad, Istiles=True)
    #             self.streams["tileWindow"+str(self.sink_count)].elements_changestate()
    #             self.sink_count = self.sink_count + 1
    #     return Gst.PadProbeReturn.OK
    #
    # def update_stream(self, rtmpsrc):
    #     """Add new stream on existing stream."""
    #     self.stop_streaming(rtmpsrc)
    #
    # def stop_streaming(self, user_data):
    #     """Stop stream and Set Video Mix to NULL."""
    #     self.videomix.get_static_pad('src').add_probe(Gst.PadProbeType.BLOCK_DOWNSTREAM, self.videomix_block_cb, user_data)
    #
    # def videomix_block_cb(self, pad, info, user_data):
    #     """Callback to handle video mix."""
    #     pad.remove_probe(info.id)
    #     self.x264enc.get_static_pad("src").add_probe(Gst.PadProbeType.BLOCK | Gst.PadProbeType.EVENT_DOWNSTREAM, self.x264enc_block_cb, user_data)
    #     self.videomix.get_static_pad('sink_0').send_event(Gst.Event.new_eos())
    #     return Gst.PadProbeReturn.OK
    #
    # def x264enc_block_cb(self, pad, info, user_data):
    #     """Callback to handle x264 enc."""
    #     EventType = info.get_event().type
    #     if(EventType != Gst.EventType.EOS):
    #         return Gst.PadProbeReturn.OK
    #
    #     pad.remove_probe(info.id)
    #     self.videomix.set_state(Gst.State.NULL)
    #     for objects in self.streams.itervalues():
    #         objects.pause_turbine()
    #
    #     # self.streams["tileWindow_u"] = turbine.turbine(pipeline=self.pipeline, rtmp_location=user_data, videocap=self.tileWindow_cap, mix_sink=self.videomix, Istiles=True)
    #     self.streams["tileWindow"].elements_changestate()
    #     self.videomix.set_state(Gst.State.PLAYING)
    #
    #     # self.streams ["tileWindow_u"].elements_changestate()
    #     return Gst.PadProbeReturn.DROP

    def cb_message(self, bus, msg, data):
        """callback to catch messages flowing on the powerhouse."""
        if (msg.type == Gst.MessageType.ERROR):
            err, debug = msg.parse_error()
            print >> sys.stderr, ("Error: {0}".format(err.message))
            self.pipeline.set_state(Gst.State.READY)
            self.main_loop.quit()

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
