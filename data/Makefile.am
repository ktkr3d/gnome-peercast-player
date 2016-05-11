SUBDIRS = icons ui 

desktopdir = $(datadir)/applications
desktop_DATA = gnome-peercast-player.desktop

UPDATE_DESKTOP = update-desktop-database $(datadir)/applications || :

install-data-hook: 
	$(UPDATE_DESKTOP)
uninstall-hook: 
	$(UPDATE_DESKTOP)
	
