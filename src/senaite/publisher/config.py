# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

from senaite.publisher import senaiteMessageFactory as _

PAPERFORMATS = {
    "A4": {
        "name": _("European A4"),
        "format": "A4",
        "dpi": 90,
        "margin_top": 40.0,
        "margin_right": 7.0,
        "margin_bottom": 23.0,
        "margin_left": 7.0,
        "orientation": "portrait",
        "page_width": 210.0,
        "page_height": 297.0,
        "header_line": False,
        "header_spacing": 35.0,

    },

    "Letter": {
        "name": _("US Letter"),
        "format": "Letter",
        "dpi": 90,
        "margin_top": 40.0,
        "margin_right": 7.0,
        "margin_bottom": 20.0,
        "margin_left": 7.0,
        "orientation": "portrait",
        "page_width": 215.9,
        "page_height": 279.4,
        "header_line": False,
        "header_spacing": 35.0,
    },
}
