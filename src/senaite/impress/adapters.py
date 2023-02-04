# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.impress import senaiteMessageFactory as _
from senaite.impress.interfaces import ICustomActionProvider
from zope.interface import implementer


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
        self.text = "<i class='fas fa-wave-square'></i>"
        self.name = ""
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = False
        self.close_after_submit = False
        self.css_class = ""

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
        self.available = view.get_allow_pdf_download()
        self.title = _("Download the generated PDF to your computer")
        self.text = "<i class='fas fa-file-download'></i>"
        self.name = "impress_download_pdf"
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = False  # bypass modal and POST directly to the URL


class SendPDFActionProvider(ActionProvider):
    """Custom action provider to send the generated PDF via email
    """
    def __init__(self, view, context, request):
        super(SendPDFActionProvider, self).__init__(view, context, request)
        self.available = view.get_allow_pdf_email_share()
        self.title = _("Share PDF via email")
        self.text = "<i class='fas fa-share-square'></i>"
        self.name = "impress_send_pdf"
        self.context_url = api.get_url(self.context)
        self.url = "{}/{}".format(self.context_url, self.name)
        self.modal = True
        self.close_after_submit = False
