# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS.
#
# SENAITE.IMPRESS is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from plone.formwidget.namedfile.converter import b64decode_file
from plone.namedfile.browser import Download
from plone.namedfile.file import NamedImage
from zope.publisher.interfaces import NotFound


class ReportLogo(Download):
    """View to serve the custom report logo from the registry
    """

    def __init__(self, context, request):
        super(ReportLogo, self).__init__(context, request)
        self.filename = None
        self.data = None
        report_logo = api.get_registry_record(
            "senaite.impress.report_logo")
        if report_logo:
            filename, data = b64decode_file(report_logo)
            data = NamedImage(data=data, filename=filename)
            self.data = data
            self.filename = filename

    def __call__(self):
        if self.data is None:
            raise NotFound(self.context, "@@report-logo",
                           self.request)
        return super(ReportLogo, self).__call__()

    def _getFile(self):
        return self.data
