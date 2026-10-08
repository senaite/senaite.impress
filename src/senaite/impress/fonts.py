# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS.
#
# SENAITE.IMPRESS is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

"""Font configuration for the PDF rendering

WeasyPrint 0.42 registers `@font-face` fonts through a generated fontconfig
file that newer fontconfig versions reject ("ambiguous constant name:
normal"). The fonts end up unregistered and the report falls back to the
system default. Instead, the fonts shipped with this package are added to
the fontconfig configuration of each rendered document, before the
configuration is bound to the Pango font map, so that they can be used by
their family name like any installed font.
"""

import glob
import os

from senaite.impress import logger
from weasyprint import fonts

FONTS_DIR = os.path.join(
    os.path.dirname(__file__), "browser", "static", "fonts")


def get_font_files():
    """Returns the paths of the TrueType fonts shipped with this package
    """
    return sorted(glob.glob(os.path.join(FONTS_DIR, "*.ttf")))


def supports_bundled_fonts():
    """Checks if WeasyPrint uses fontconfig on this platform
    """
    return hasattr(fonts, "pangoft2")


def add_font_file(config, path):
    """Adds the font file to the fontconfig configuration
    """
    if isinstance(path, unicode):
        path = path.encode(fonts.FILESYSTEM_ENCODING)
    if not fonts.fontconfig.FcConfigAppFontAddFile(config, path):
        logger.warn("Could not add font '{}' to fontconfig".format(path))


class BundledFontConfiguration(fonts.FontConfiguration):
    """Font configuration with the fonts shipped with SENAITE.IMPRESS
    """

    def __init__(self):
        ffi = fonts.ffi
        fontconfig = fonts.fontconfig
        self._filenames = []
        self._fontconfig_config = ffi.gc(
            fontconfig.FcInitLoadConfigAndFonts(),
            fontconfig.FcConfigDestroy)
        # fonts must be added before the config is bound to the font map
        for path in get_font_files():
            add_font_file(self._fontconfig_config, path)
        self.font_map = ffi.gc(
            fonts.pangocairo.pango_cairo_font_map_new_for_font_type(
                fonts.cairo.FONT_TYPE_FT),
            fonts.gobject.g_object_unref)
        fonts.pangoft2.pango_fc_font_map_set_config(
            ffi.cast("PangoFcFontMap *", self.font_map),
            self._fontconfig_config)
        # pango_fc_font_map_set_config keeps a reference to config
        fontconfig.FcConfigDestroy(self._fontconfig_config)


def get_font_config():
    """Returns a new font configuration for rendering a document
    """
    if not supports_bundled_fonts():
        return fonts.FontConfiguration()
    return BundledFontConfiguration()
