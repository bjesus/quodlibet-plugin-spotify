# -*- coding: utf-8 -*-
# Copyright 2005-2010   Joshua Kwan <joshk@triplehelix.org>,
#                       Michael Ball <michael.ball@gmail.com>,
#                       Steven Robertson <steven@strobe.cc>
#                2016   Nick Boultbee
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from gi.repository import Gtk

from quodlibet import _, config
from quodlibet.qltk import Icons, Frame
from quodlibet.qltk.entry import UndoEntry
from quodlibet.plugins.songsmenu import SongsMenuPlugin
from quodlibet.plugins.songshelpers import is_writable, each_song, is_finite

from .util import pconfig
from .widgets import SearchWindow

def config_get(key, default=None):
    return config.get('plugins', 'spotify_%s' % key, default)

class MyBrainz(SongsMenuPlugin):
    PLUGIN_ID = "Spotify lookup"
    PLUGIN_NAME = _("Spotify Lookup")
    PLUGIN_ICON = Icons.MEDIA_OPTICAL
    PLUGIN_DESC = _('Re-tags an album based on a Spotify search.')

    plugin_handles = each_song(is_writable, is_finite)

    def plugin_albums(self, albums):
        if not albums:
            return

        def win_finished_cb(widget, *args):
            if albums:
                start_processing(albums.pop(0))
            else:
                self.plugin_finish()

        def start_processing(disc):
            win = SearchWindow(self.plugin_window, disc)
            win.connect("destroy", win_finished_cb)
            win.show()

        start_processing(albums.pop(0))

    @classmethod
    def PluginPreferences(self, win):

        def id_entry_changed(entry):
            config.set('plugins', 'spotify_client_id', id_entry.get_text())

        id_label = Gtk.Label(label=_("_Client ID:"), use_underline=True)
        id_entry = UndoEntry()
        id_entry.set_text(config_get('client_id', ''))
        id_entry.connect('changed', id_entry_changed)
        id_label.set_mnemonic_widget(id_entry)

        id_hbox = Gtk.HBox()
        id_hbox.set_spacing(6)
        id_hbox.pack_start(id_label, False, True, 0)
        id_hbox.pack_start(id_entry, True, True, 0)


        def secret_entry_changed(entry):
            config.set('plugins', 'spotify_client_secret', secret_entry.get_text())

        secret_label = Gtk.Label(label=_("_Client secret:"), use_underline=True)
        secret_entry = UndoEntry()
        secret_entry.set_text(config_get('client_secret', ''))
        secret_entry.connect('changed', secret_entry_changed)
        secret_label.set_mnemonic_widget(secret_entry)

        secret_hbox = Gtk.HBox()
        secret_hbox.set_spacing(6)
        secret_hbox.pack_start(secret_label, False, True, 0)
        secret_hbox.pack_start(secret_entry, True, True, 0)

        vb = Gtk.VBox()
        vb.set_spacing(8)
        vb.pack_start(id_hbox, True, True, 0)
        vb.pack_start(secret_hbox, True, True, 0)

        return Frame(_("Account"), child=vb)

        # items = [
        #     ('year_only', _('Only use year for "date" tag')),
        #     ('albumartist', _('Write "_albumartist" when needed')),
        #     ('artist_sort', _('Write sort tags for artist names')),
        #     ('standard', _('Write _standard MusicBrainz tags')),
        #     ('labelid2', _('Write "labelid" tag')),
        # ]

        # new_items = [
        #     ('client_id', _('ID')),
        #     ('client_secret', _('Secret'))
        # ]

        # vb = Gtk.VBox()
        # vb.set_spacing(8)

        # for key, label in items:
        #     ccb = pconfig.ConfigCheckButton(label, key, populate=True)
        #     vb.pack_start(ccb, True, True, 0)
        
        # for key, label in new_items:
        #     ccb = pconfig.ConfigCheckButton(label, key, populate=True)
        #     vb.pack_start(ccb, True, True, 0)

        # return vb
