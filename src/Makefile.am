SUBDIRS = gpp

bin_SCRIPTS = gnome-peercast-player
CLEANFILES = $(bin_SCRIPTS)
EXTRA_DIST = gnome-peercast-player.in

do_substitution = sed -e 's,[@]pythondir[@],$(pythondir),g' \
	-e 's,[@]pkgdatadir[@],$(pkgdatadir),g' \
	-e 's,[@]PACKAGE[@],$(PACKAGE),g' \
	-e 's,[@]VERSION[@],$(VERSION),g' 

gnome-peercast-player: gnome-peercast-player.in Makefile
	$(do_substitution) < $(srcdir)/gnome-peercast-player.in > gnome-peercast-player
	chmod +x gnome-peercast-player
