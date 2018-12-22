# -*- coding: utf-8 -*-
# Copyright 2016 Christoph Reiter
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

try:
    # https://github.com/alastair/python-musicbrainzngs/issues/157
    # Work around warnings getting enabled in musicbrainzngs
    import warnings
    f = list(warnings.filters)
    import spotipy
    import spotipy.oauth2 as oauth2
    warnings.filters[:] = f
except ImportError:
    from quodlibet import plugins
    raise plugins.MissingModulePluginException("spotipy")

from quodlibet import app
from quodlibet import const
from quodlibet import util
from quodlibet import config


VARIOUS_ARTISTS_ARTISTID = '89ad4ac3-39f7-470e-963a-56509c546377'


global_releases = {}

def connect():
    client_id = config.get('plugins', 'spotify_client_id')
    client_secret = config.get('plugins', 'spotify_client_secret')

    credentials = oauth2.SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret)

    token = credentials.get_access_token()
    return spotipy.Spotify(auth=token)


def is_mbid(id_):
    return len(id_) == 36


def search_releases(query):
    """Returns a list of ReleaseResult or raises MusicBrainzError"""

    # musicbrainzngs.set_useragent(app.name, const.VERSION)
    # data = [Release(r) for r in
    #         musicbrainzngs.search_releases(query)["release-list"]]

    spotify = connect()

    data = [Release(r) for r in
            spotify.search(q=query, type="album")["albums"]['items']]
    return data


def _get_release(release_id):
    """Returns a release containing all recordings and artists or raises
    MusicBrainzError
    """

    # assert is_mbid(release_id)
    if not release_id in global_releases:
        spotify = connect()
        global_releases[release_id] = spotify.album(release_id)

    return global_releases[release_id]


class Artist(object):

    def __init__(self, name, sort_name, id_):
        self.name = name
        self.sort_name = sort_name
        self.id = id_  # MusicBrainz Artist ID / Album Artist ID

    @property
    def is_various(self):
        return self.id == VARIOUS_ARTISTS_ARTISTID

    @classmethod
    def from_credit(cls, mbcredit):
        artists = []
        for credit in mbcredit:
            # try:
            #     artist = credit["artist"]
            # except TypeError:
            #     # join strings
            #     pass
            # else:
            artists.append(
                Artist(credit["name"], credit["name"], credit["id"]))
        return artists


class ReleaseTrack(object):
    """Part of a Release, combines per track and per medium data"""

    def __init__(self, mbtrack, track_count):
        self._mbtrack = mbtrack
        self.track_count = track_count

    @property
    def id(self):
        """MusicBrainz release track ID"""

        return self._mbtrack["id"]

    @property
    def artists(self):
        return Artist.from_credit(self._mbtrack["artists"])

    @property
    def title(self):
        return self._mbtrack["name"]

    @property
    def tracknumber(self):
        return self._mbtrack["track_number"]


class Release(object):

    def __init__(self, mbrelease):
        self._mbrelease = mbrelease

    @property
    def labelid(self):
        return self._mbrelease.get("label", u"")

    @property
    def id(self):
        """MusicBrainz release ID"""

        return self._mbrelease["id"]

    @property
    def date(self):
        return self._mbrelease.get("release_date", u"")

    @property
    def medium_format(self):
        # for medium in self._mbrelease["medium-list"]:
        #     format_ = medium.get("format", u"")
        #     if format_:
        #         formats.append(format_)
        formats = ["CD"]
        return u"/".join(formats)

    @property
    def country(self):
        return self._mbrelease.get("country", u"")

    @property
    def disc_count(self):
        return 1

    @property
    def track_count(self):
        """Number of tracks for all included mediums"""

        track_count = 0
        try:
            track_count = self._mbrelease['total_tracks']
        except:
            pass
        return track_count

    @property
    def tracks(self):
        tracks = []
        # for medium in self._mbrelease["medium-list"]:
        #     disc = medium["position"]
        #     title = medium.get("title", u"")
        #     track_count = medium["track-count"]
        #     if "pregap" in medium:
        #         track_count += 1
        #         tracks.append(
        #             ReleaseTrack(medium["pregap"], disc, track_count, title))
        #     for track in medium["track-list"]:
        #         tracks.append(ReleaseTrack(track, disc, track_count, title))
        for track in global_releases[self._mbrelease['id']]['tracks']['items']:
            tracks.append(ReleaseTrack(track, self._mbrelease['total_tracks']))
        return tracks

    @property
    def title(self):
        return self._mbrelease["name"]

    @property
    def is_single_artist(self):
        """If all tracks have the same artists as the release"""

        ids = [a.id for a in self.artists]
        for track in self.tracks:
            track_ids = [a.id for a in track.artists]
            if ids != track_ids:
                return False
        return True

    @property
    def is_various_artists(self):
        artists = self.artists
        return len(artists) == 1 and artists[0].is_various

    @property
    def artists(self):
        return Artist.from_credit(self._mbrelease["artists"])

    def fetch_full(self):
        """Returns a new Release instance containing more info
        or raises MusicBrainzError

        This method is blocking..
        """

        return Release(_get_release(self.id))
