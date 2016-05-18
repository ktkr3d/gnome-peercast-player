#!/usr/bin/python

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import urllib2

# vlc
import time
import sys
import vlc

# webkit
import gi
gi.require_version('WebKit', '3.0')
from gi.repository import WebKit

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
        req = urllib2.Request("http://peercast.takami98.net/multi-yp/index.txt")
        res = urllib2.urlopen(req)
        arrayChannelData = res.read().splitlines()
        for i in range(0, len(arrayChannelData)):
            channelData = arrayChannelData[i].split("<>")
            channel = channelData[0].replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&quot;", '"').replace("&#039;", "'")
            listeners = int(channelData[6])
            print(channel)
            streamurl = "mmsh://localhost:7144/stream/" + channelData[1] + "?tip=" + channelData[2]
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

    	self.window = builder.get_object("window")
    	headerbar = builder.get_object("headerbar")
    	self.window.set_titlebar(headerbar)

    	# vlc
    	stream = builder.get_object("stream")
    	stream.__vlc = VLCWidget()
    	stream.add(stream.__vlc)
    	stream.player = stream.__vlc.player

    	# webkit
    	web = builder.get_object("web")
    	web_view = WebKit.WebView()
    	web_url = "http://localhost:7144/"
        settings = web_view.get_settings()
        settings.set_property('user-stylesheet-uri', 'user-style.css')
        settings.set_property('enable-universal-access-from-file-uris', True)
        web_view.set_settings(settings)
        #web_view.connect("load-started", self.on_load_started)
        #web_view.connect("load-finished", self.on_load_finished)
        #web_view.connect("title-changed", self.on_title_changed)
        #web_view.connect("hovering-over-link", self.on_hovering_over_link)
    	web_view.open(web_url)
    	web.add(web_view)

        # status bar
    	statusbar = builder.get_object("statusbar")

        Handler.headerbar = headerbar
        Handler.web_view = web_view
        Handler.stream = stream
        Handler.statusbar = statusbar

    def quit(self, widget=None, data=None):
        Gtk.main_quit()

    def run(self):
        self.window.show_all()
        Gtk.main()
