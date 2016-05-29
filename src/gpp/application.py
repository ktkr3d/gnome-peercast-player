#!/usr/bin/python

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, WebKit, Gdk, Notify

import os
import urllib2
import time
import sys
import socket
import vlc
import pickle

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
        self.set_size_request(400, 240)

class Handler:
    def on_window_delete_event(self, *args):
        Gtk.main_quit(*args)

    def on_button_quit_clicked(self, window):
        Gtk.main_quit(window)

    def on_button_playback_clicked(self, stream):
        if self.web_url == self.peercast_url:
            self.web_url = self.contact_url
        else:
            self.web_url = self.peercast_url
        self.web_view.open(self.web_url)

    def on_button_about_clicked(self, dialog_about):
        dialog_about.run()
        dialog_about.hide()

    def on_button_preferences_clicked(self, dialog_preferences):
        self.entry_peercast_server.set_text(self.conf["peercast_server"])
        self.spinbutton_peercast_port.set_value(int(self.conf["peercast_port"]))
        dialog_preferences.run()
        dialog_preferences.hide()
        self.conf["peercast_server"] = self.entry_peercast_server.get_text()
        self.conf["peercast_port"] = str(self.spinbutton_peercast_port.get_value_as_int())
        pickle.dump(self.conf, open(self.path_conf, "w"))

    def on_button_refresh_clicked(self, liststore):
        liststore.clear()
        req = urllib2.Request("http://peercast.takami98.net/multi-yp/index.txt")
        res = urllib2.urlopen(req)
        arrayChannelData = res.read().splitlines()
        for i in range(0, len(arrayChannelData)):
            channelData = arrayChannelData[i].split("<>")
            channel = channelData[0].replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&quot;", '"').replace("&#039;", "'")
            comment = "[" + channelData[4] + " - "+ channelData[5] + "]" + channelData[17]
            comment = comment.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&").replace("&quot;", '"').replace("&#039;", "'")
            listeners = int(channelData[6])
            print(channel)
            if channelData[9] in ["WMV","WMA"]:
                streamurl = "mmsh://" + self.peercast_server + ":" + self.peercast_port + "/stream/" + channelData[1] + "?tip=" + channelData[2]
            else:
                streamurl = "http://" + self.peercast_server + ":" + self.peercast_port + "/stream/" + channelData[1] + "?tip=" + channelData[2]
            liststore.append([channel,listeners,streamurl,channelData[3],channelData[9],int(channelData[8]),comment,channelData[15]])
        context_id = self.statusbar.get_context_id("message")
        message_id = self.statusbar.push(context_id, "channels: " + str(len(arrayChannelData)))

    def on___glade_unnamed_28_row_activated(self, liststore, treepath, treeviewcolumn):
        iter = liststore.get_iter(treepath)
        stream_url = liststore[iter][2]
        print(stream_url)
    	self.stream.player.set_media(instance.media_new(stream_url))
    	self.stream.player.play()
        self.contact_url = liststore[iter][3]
        self.web_url = self.contact_url
    	self.web_view.open(self.web_url)
        self.headerbar.set_title(liststore[iter][0])
        self.headerbar.set_subtitle(liststore[iter][6])

    def on_button_fullscreen_clicked(self, window):
        self.statusbar.hide()
        window.fullscreen()
        print("fullscreen button clicked")

    def on_window_window_state_event(self, widget, event, data=None):
        self.window_current_state = event.new_window_state

    def toggle_fullscreen(self):
        if self.window_current_state & Gdk.WindowState.FULLSCREEN:
            self.statusbar.show()
            self.window.unfullscreen()
        else:
            self.statusbar.hide()
            self.window.fullscreen()

    def on_window_key_press_event(self, widget, event):
        key = event.keyval
        if key == 0xffc8:
            self.toggle_fullscreen()
        return False

    def on_checkbutton_list_toggled(self, list):
        if self.checkbutton_list.get_active():
            list.show_all()
        else:
            list.hide()

    def on_checkbutton_web_toggled(self, web):
        if self.checkbutton_web.get_active():
            web.show_all()
        else:
            web.hide()

    def on_togglebutton_find_toggled(self, searchentry):
        if self.togglebutton_find.get_active():
            searchentry.show()
            searchentry.grab_focus_without_selecting()
        else:
            searchentry.hide()

    def on_searchentry_changed(self, liststore):
        self.filter.refilter()
        print("on search entry")

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

        # objects
    	self.window = builder.get_object("window")
    	self.searchentry = builder.get_object("searchentry")
    	stream = builder.get_object("stream")
    	web = builder.get_object("web")
    	statusbar = builder.get_object("statusbar")
    	Handler.togglebutton_find = builder.get_object("togglebutton_find")
    	Handler.checkbutton_list = builder.get_object("checkbutton_list")
    	Handler.checkbutton_web = builder.get_object("checkbutton_web")
    	Handler.entry_peercast_server = builder.get_object("entry_peercast_server")
    	Handler.spinbutton_peercast_port = builder.get_object("spinbutton_peercast_port")

        # header bar
    	headerbar = builder.get_object("headerbar")
    	self.window.set_titlebar(headerbar)

    	# vlc
    	stream.__vlc = VLCWidget()
    	stream.add(stream.__vlc)
    	stream.player = stream.__vlc.player

        # load settings
        path_conf = os.environ["HOME"] + "/.gnome-peercast-player"
        print(path_conf)
        if os.path.exists(path_conf):
            conf = pickle.load(open(path_conf))
            peercast_server = conf["peercast_server"]
            peercast_port = conf["peercast_port"]
        else:
            peercast_server = "localhost"
            peercast_port = "7144"

        # save settings
        conf = {"version": "0.0.3", "peercast_server": peercast_server, "peercast_port": peercast_port}
        Handler.conf = conf
        Handler.path_conf = path_conf
        pickle.dump(conf, open(path_conf, "w"))

    	# webkit
    	web_view = WebKit.WebView()
    	peercast_url = "http://" + peercast_server + ":" + peercast_port

        # Custom Stylesheet
    	style_file = os.path.join(self.pkgdatadir, "ui", "style.css")
        web_view.get_settings().set_property('enable-universal-access-from-file-uris', True)
        web_view.get_settings().set_property('user-stylesheet-uri', style_file)

        # check peercast server & port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((peercast_server, int(peercast_port)))
            s.close()
        except socket.error as e:
            Notify.init('GNOME Peercast Player')
            notification = Notify.Notification.new(
                    'Cannot connect to peercast server.',
                    'port (%s:%s) is not open.' % (peercast_server, peercast_port),
                    'dialog-warning'
                )
            notification.show()

        web_url = peercast_url
    	web_view.open(web_url)
    	web.add(web_view)

        # list

        # handler
        Handler.window = self.window
        Handler.headerbar = headerbar
        Handler.web_view = web_view
        Handler.web_url = web_url
        Handler.contact_url = peercast_url
        Handler.stream = stream
        Handler.statusbar = statusbar
        Handler.peercast_server = peercast_server
        Handler.peercast_port = peercast_port
        Handler.peercast_url = peercast_url

    	liststore = builder.get_object("liststore1")
    	liststore_filter = builder.get_object("liststore1_filter")
        self.keyword = ""
        #Handler.filter = liststore.filter_new()
        liststore_filter.set_visible_func(self.filter_func)
        Handler.filter = liststore_filter
    	liststore.set_sort_column_id(1, True)
        Handler.on_button_refresh_clicked(Handler(), liststore)

        self.window.set_position(Gtk.WindowPosition.CENTER)

    def filter_func(self, model, iter, keyword):
        self.keyword = self.searchentry.get_text()
        print("filter_func has called. %s" % self.keyword)
        if self.keyword == "":
            print("keyword is empty.")
            return True
        else:
            return self.keyword.lower() in model[iter][0].lower() or self.keyword.lower() in model[iter][6].lower()
            #return False

    def quit(self, widget=None, data=None):
        Gtk.main_quit()

    def run(self):
        self.window.show_all()
        self.searchentry.hide()
        Gtk.main()
