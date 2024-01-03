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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from senaite.impress import senaiteMessageFactory as _
from senaite.impress.interfaces import ICustomActionProvider
from senaite.impress.interfaces import IGroupKeyProvider
from zope.interface import implementer


@implementer(IGroupKeyProvider)
class GroupKeyProvider(object):
    """Provide a grouping key for PDF separation
    """
    def __init__(self, context):
        self.context = context

    def __call__(self):
        try:
            # split samples from different clients
            return self.context.getClientUID()
        except AttributeError:
            return "_nogroup_"


@implementer(ICustomActionProvider)
class ActionProvider(object):
    """Base class for new action providers
    """
    def __init__(self, view, context, request):
        self.view = view
        self.context = context
        self.request = request
        # see senaite.impress.interfaces.ICustomFormProvider
        self.title = ""
        self.text = "<i class='fas fa-wave-square'></i>"
        self.name = ""
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = False
        self.close_after_submit = False
        self.css_class = ""

    def available(self):
        return False

    def get_action_data(self):
        return {
            "name": self.name,
            "title": self.title,
            "text": self.text,
            "url": self.url,
            "modal": self.modal,
            "close_after_submit": self.close_after_submit,
            "css_class": self.css_class,
        }


class DownloadPDFActionProvider(ActionProvider):
    """Custom action provider to download the report PDF directly
    """
    def __init__(self, view, context, request):
        super(DownloadPDFActionProvider, self).__init__(view, context, request)
        self.title = _("Download the generated PDF to your computer")
        self.text = "<i class='fas fa-file-download'></i>"
        self.name = "impress_download_pdf"
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = False  # bypass modal and POST directly to the URL

    def available(self):
        return self.view.get_allow_pdf_download()


class SendPDFActionProvider(ActionProvider):
    """Custom action provider to send the generated PDF via email
    """
    def __init__(self, view, context, request):
        super(SendPDFActionProvider, self).__init__(view, context, request)
        self.title = _("Share PDF via email")
        self.text = "<i class='fas fa-share-square'></i>"
        self.name = "impress_send_pdf"
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = True
        self.close_after_submit = False

    def available(self):
        return self.view.get_allow_pdf_email_share()
