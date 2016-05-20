#!/usr/bin/python

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, WebKit, Gdk

import os
import urllib2
import time
import sys
import vlc

from gettext import gettext as _

instance = vlc.Instance()

class VLCWidget(Gtk.DrawingArea):
    def __init__(self, *p):
        Gtk.DrawingArea.__init__(self)
        self.player = instance.media_player_new()
        def handle_embed(*args):
            thewindow = self.get_window()
            if sys.platform == 'win32':
                self.player.set_hwnd(self.window.handle)
            else:
                 self.player.set_xwindow(thewindow.get_xid())
            return True
        self.connect("map", handle_embed)
        self.set_size_request(400, 300)

class Handler:

    def on_window_delete_event(self, *args):
        Gtk.main_quit(*args)

    def on_button_quit_clicked(self, window):
        Gtk.main_quit(window)

    def on_button_playback_clicked(self, stream):
        self.__stream = stream
    	stream_url = "https://github.com/ktkr3d/ktkr3d.github.io/blob/master/images/galaxias.mp4?raw=true"
    	stream.player.set_media(instance.media_new(stream_url))
    	stream.player.play()

    def on_button_about_clicked(self, dialog_about):
        dialog_about.run()
        dialog_about.hide()

    def on_button_preferences_clicked(self, dialog_preferences):
        dialog_preferences.run()
        dialog_preferences.hide()

    def on_button_refresh_clicked(self, liststore):
        liststore.clear()
        req = urllib2.Request("http://peercast.takami98.net/multi-yp/index.txt")
        res = urllib2.urlopen(req)
        arrayChannelData = res.read().splitlines()
        for i in range(0, len(arrayChannelData)):
            channelData = arrayChannelData[i].split("<>")
            channel = channelData[0].replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&quot;", '"').replace("&#039;", "'")
            listeners = int(channelData[6])
            print(channel)
            streamurl = "mmsh://" + self.peercast_server + ":" + self.peercast_port + "/stream/" + channelData[1] + "?tip=" + channelData[2]
            liststore.append([channel,listeners,streamurl,channelData[3],channelData[9],int(channelData[8]),channelData[4]+channelData[5]+channelData[17],channelData[15]])
        context_id = self.statusbar.get_context_id("message")
        message_id = self.statusbar.push(context_id, "channels: " + str(len(arrayChannelData)))

    def on___glade_unnamed_28_row_activated(self, liststore, treepath, treeviewcolumn):
        iter = liststore.get_iter(treepath)
        stream_url = liststore[iter][2]
        print(stream_url)
    	self.stream.player.set_media(instance.media_new(stream_url))
    	self.stream.player.play()
        web_url = liststore[iter][3]
    	self.web_view.open(web_url)
        self.headerbar.set_subtitle(liststore[iter][0])

    def on_button_fullscreen_clicked(self, window):
        window.fullscreen()
        print("fullscreen button clicked")

    def on_window_window_state_event(self, widget, event, data=None):
        self.window_current_state = event.new_window_state

    def toggle_fullscreen(self):
        if self.window_current_state & Gdk.WindowState.FULLSCREEN:
            self.window.unfullscreen()
        else:
            self.window.fullscreen()

    def on_window_key_press_event(self, widget, event):
        key = event.keyval
        if key == 0xffc8:
            self.toggle_fullscreen()
        return False

class Application(object):
    def on_button_preferences_clicked(self, dialog_preferences):
        dialog_preferences.run()
        dialog_preferences.hide()

    def __init__(self, *args, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self._create_main_window()

    def _create_main_window(self):
    	builder = Gtk.Builder()
    	ui_file = os.path.join(self.pkgdatadir, "ui", "main_window.ui")
    	builder.add_from_file(ui_file)
    	builder.connect_signals(Handler())

        # objects
    	self.window = builder.get_object("window")
    	stream = builder.get_object("stream")
    	web = builder.get_object("web")
    	statusbar = builder.get_object("statusbar")

        # header bar
    	headerbar = builder.get_object("headerbar")
    	self.window.set_titlebar(headerbar)

    	# vlc
    	stream.__vlc = VLCWidget()
    	stream.add(stream.__vlc)
    	stream.player = stream.__vlc.player

        peercast_server = "192.168.0.2"
        peercast_port = "7144"

    	# webkit
    	web_view = WebKit.WebView()
    	web_url = "http://" + peercast_server + ":" + peercast_port

        """
        web_view.preferences().setUserStyleSheetEnabled_(objc.YES)
        print web_view.preferences().userStyleSheetEnabled()
        webview.preferences().setUserStyleSheetLocation_("user-style.css")
        print webview.preferences().userStyleSheetLocation()
        """
        web_view.get_settings().set_property('enable-universal-access-from-file-uris', True)
        web_view.get_settings().set_property('user-stylesheet-uri', 'file:///mnt/common/repos/gnome-peercast-player/style.css')
        #web_view.connect("load-started", self.on_load_started)
        #web_view.connect("load-finished", self.on_load_finished)
        #web_view.connect("title-changed", self.on_title_changed)
        #web_view.connect("hovering-over-link", self.on_hovering_over_link)

    	web_view.open(web_url)
    	web.add(web_view)

        # accel

        # handler
        Handler.window = self.window
        Handler.headerbar = headerbar
        Handler.web_view = web_view
        Handler.stream = stream
        Handler.statusbar = statusbar
        Handler.peercast_server = peercast_server
        Handler.peercast_port = peercast_port

    def quit(self, widget=None, data=None):
        Gtk.main_quit()

    def run(self):
        self.window.show_all()
        Gtk.main()
