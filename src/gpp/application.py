#!/usr/bin/python

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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
        self.set_size_request(640, 360)
#        self.set_size_request(640, 660)


class Handler:
    def on_window_delete_event(self, *args):
        Gtk.main_quit(*args)
    def on_button_quit_clicked(self, window):
        Gtk.main_quit(window)
    def on_button_about_clicked(self, dialog_about):
        dialog_about.run()
        dialog_about.destroy()
    def on_button_preferences_clicked(self, dialog_preferences):
        dialog_preferences.run()
        dialog_preferences.destroy()

class Application(object):
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
	#stream.pack_start(vlc, True, True, 0)
	stream.player=stream.__vlc.player
	stream_url = "https://github.com/ktkr3d/ktkr3d.github.io/blob/master/images/galaxias.mp4?raw=true"
	#stream_url = "mmsh://localhost:7144/stream/ ..."
	#stream_url = "http://localhost:7144/stream/ ..."
	stream.player.set_media(instance.media_new(stream_url))

	# list
	store_list = builder.get_object("store_list")
	store_list.append(["channel",100])

	# webkit
	web = builder.get_object("web")
	web_view = WebKit.WebView()
	web_url = "https://github.com/ktkr3d/gnome-peercast-player"
	#web_url = "http://localhost:7144/"
	web_view.open(web_url)
	web.add(web_view)
	time.sleep(1)
	stream.__vlc.player.play()
    
    def quit(self, widget=None, data=None):
        Gtk.main_quit()
        
    def run(self):
        self.window.show_all()
        Gtk.main()

