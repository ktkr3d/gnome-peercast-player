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

builder = Gtk.Builder()
builder.add_from_file("gpp_main.glade")
builder.connect_signals(Handler())

window = builder.get_object("window")
headerbar = builder.get_object("headerbar")
window.set_titlebar(headerbar)

# vlc
stream = builder.get_object("stream")
stream.__vlc = VLCWidget()
stream.add(stream.__vlc)
#stream.pack_start(vlc, True, True, 0)
stream.player=stream.__vlc.player
stream_url = "./galaxias.mp4"
#stream_url = "mmsh://localhost:7144/stream/ ..."
#stream_url = "http://localhost:7144/stream/ ..."
stream.player.set_media(instance.media_new(stream_url))

# list
store_list = builder.get_object("store_list")
store_list.append(["channel",100])

# webkit
web = builder.get_object("web")
web_view = WebKit.WebView()
web_url = "http://localhost:7144/"
web_view.open(web_url)
web.add(web_view)

window.show_all()
time.sleep(1)
stream.__vlc.player.play()

Gtk.main()
