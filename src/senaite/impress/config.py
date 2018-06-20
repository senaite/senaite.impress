# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from collections import OrderedDict

# Value of key `format` must match the allowed CSS size attribute:
# https://developer.mozilla.org/en-US/docs/Web/CSS/@page/size
PAPERFORMATS = OrderedDict((
    ("A3", {
        "name": "DIN A3",
        "format": "A3",
        "margin_top": 20.0,
        "margin_right": 20.0,
        "margin_bottom": 20.0,
        "margin_left": 20.0,
        "page_width": 297.0,
        "page_height": 420.0,

    }),

    ("A4", {
        "name": "DIN A4",
        "format": "A4",
        "margin_top": 10.0,
        "margin_right": 20.0,
        "margin_bottom": 10.0,
        "margin_left": 20.0,
        "page_width": 210.0,
        "page_height": 297.0,

    }),

    ("A5", {
        "name": "DIN A5",
        "format": "A5",
        "margin_top": 15.0,
        "margin_right": 15.0,
        "margin_bottom": 15.0,
        "margin_left": 15.0,
        "page_width": 148.0,
        "page_height": 210.0,
    }),

    ("ledger", {
        "name": "US Ledger",
        "format": "ledger",
        "margin_top": 20.0,
        "margin_right": 20.0,
        "margin_bottom": 20.0,
        "margin_left": 20.0,
        "page_width": 279.0,
        "page_height": 432.0,
    }),

    ("legal", {
        "name": "US Legal",
        "format": "legal",
        "margin_top": 20.0,
        "margin_right": 20.0,
        "margin_bottom": 20.0,
        "margin_left": 20.0,
        "page_width": 216.0,
        "page_height": 356.0,
    }),

    ("letter", {
        "name": "US Letter",
        "format": "letter",
        "margin_top": 20.0,
        "margin_right": 20.0,
        "margin_bottom": 20.0,
        "margin_left": 20.0,
        "page_width": 215.9,
        "page_height": 279.4,
    }),
))
