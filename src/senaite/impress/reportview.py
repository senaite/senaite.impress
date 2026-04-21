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

from bika.lims import api
from senaite.impress.interfaces import IReportView
from zope.interface import implements

DEFAULT_LOGO = "++plone++senaite.core.static/images/senaite.svg"


class ReportView(object):
    """Generic Report View

    Note: This is also the base class for the Multi Report View
    """
    implements(IReportView)

    def __init__(self, *args, **kwargs):
        # needed for template rendering
        self.context = api.get_portal()

    def render(self, template, **kw):
        raise NotImplementedError(
            "Must be implemented by subclass")

    def get_report_logo_url(self):
        """Returns the URL of the report logo

        Falls back to the default SENAITE logo if no custom
        logo has been uploaded in the impress control panel.
        """
        report_logo = api.get_registry_record(
            "senaite.impress.report_logo")
        portal_url = api.get_portal().absolute_url()
        if report_logo:
            return "{}/@@report-logo".format(portal_url)
        return "{}/{}".format(portal_url, DEFAULT_LOGO)

    def get_page_margins(self):
        """Returns per-template margin overrides

        Override this method in add-on report views to provide
        custom margins for specific templates.

        Returns a dict with any combination of:
            margin_top, margin_right, margin_bottom, margin_left

        Only keys present in the returned dict will override
        the cascade (paperformat defaults -> registry globals).
        Return an empty dict to use the default cascade.
        """
        return {}
