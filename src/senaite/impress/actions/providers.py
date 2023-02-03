# -*- coding: utf-8 -*-

import collections

import six

from bika.lims import api
from Products.Five.browser import BrowserView


class CustomAction(BrowserView):
    """Base class for custom actions
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.uids = self.get_uids_from_request()

    def get_uids_from_request(self):
        """Returns a list of uids from the request
        """
        uids = self.request.get("uids", "")
        if isinstance(uids, six.string_types):
            uids = uids.split(",")
        unique_uids = collections.OrderedDict().fromkeys(uids).keys()
        return filter(api.is_uid, unique_uids)


class DownloadPDF(CustomAction):
    """Download Action
    """
    def __init__(self, context, request):
        super(DownloadPDF, self).__init__(context, request)

    def __call__(self):
        pdf = self.request.get("pdf")
        data = "".join([x for x in pdf.xreadlines()])
        return self.download(data)

    def download(self, data, mime_type="application/pdf"):
        # NOTE: The filename does not matter, because we are downloading
        #       the PDF in the Ajax handler with createObjectURL
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=report.pdf")
        self.request.response.setHeader("Content-Type", mime_type)
        self.request.response.setHeader("Content-Length", len(data))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(data)
