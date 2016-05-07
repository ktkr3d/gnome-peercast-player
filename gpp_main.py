import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import time
import sys
import vlc
import vlcwidget

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


class Handler:
    def on_window_delete_event(self, *args):
        Gtk.main_quit(*args)
    def on_menu_clicked(self, popover):
        popover.show_all()

builder = Gtk.Builder()
builder.add_from_file("gpp_main.glade")
builder.connect_signals(Handler())

window = builder.get_object("window")
headerbar = builder.get_object("headerbar")
window.set_titlebar(headerbar)

# vlc staff
stream = builder.get_object("stream")
stream.__vlc = VLCWidget()
stream.add(stream.__vlc)
#stream.pack_start(vlc, True, True, 0)
stream.player=stream.__vlc.player

stream.player.set_media(instance.media_new("./galaxias.mp4"))
#time.sleep(3)

window.show_all()
time.sleep(1)
stream.__vlc.player.play()

Gtk.main()
