# -*- coding: utf-8 -*-

from zope.interface import implementer
from senaite.impress.interfaces import ICustomActionProvider
from bika.lims import api


@implementer(ICustomActionProvider)
class DownloadPDFActionProvider(object):
    """Custom action provider to download the report PDF directly
    """

    def __init__(self, view, context, request):
        self.view = view
        self.context = context
        self.request = request
        self.available = view.get_allow_pdf_download()
        self.title = "PDF"
        self.name = "impress_download_pdf"
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)

    def get_action_data(self):
        return {
            "name": self.name,
            "title": self.title,
            "url": self.url,
            "direct_submit": True,
        }
