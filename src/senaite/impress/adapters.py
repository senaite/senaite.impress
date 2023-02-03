# -*- coding: utf-8 -*-

from zope.interface import implementer
from senaite.impress.interfaces import ICustomActionProvider
from bika.lims import api


@implementer(ICustomActionProvider)
class ActionProvider(object):
    """Base class for new action providers
    """
    def __init__(self, view, context, request):
        self.view = view
        self.context = context
        self.request = request
        # see senaite.impress.interfaces.ICustomFormProvider
        self.available = False
        self.title = ""
        self.name = ""
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = False

    def get_action_data(self):
        return {
            "name": self.name,
            "title": self.title,
            "url": self.url,
            "modal": self.modal,
        }


class DownloadPDFActionProvider(ActionProvider):
    """Custom action provider to download the report PDF directly
    """
    def __init__(self, view, context, request):
        super(DownloadPDFActionProvider, self).__init__(view, context, request)
        self.available = view.get_allow_pdf_download()
        self.title = "PDF"
        self.name = "impress_download_pdf"
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = False  # bypass modal and POST directly to the URL
