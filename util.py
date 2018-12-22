# -*- coding: utf-8 -*-
# Copyright 2005-2010   Joshua Kwan <joshk@triplehelix.org>,
#                       Michael Ball <michael.ball@gmail.com>,
#                       Steven Robertson <steven@strobe.cc>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

from quodlibet.plugins import PluginConfig


def get_config():
    pc = PluginConfig("brainz")

    defaults = pc.defaults
    defaults.set("client_id", "")
    defaults.set("client_secret", "")

    return pc


pconfig = get_config()
