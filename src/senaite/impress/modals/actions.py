# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.browser.modals import Modal


class DownloadPDF(Modal):
    template = ViewPageTemplateFile("templates/download_pdf.pt")

    def __init__(self, context, request):
        super(DownloadPDF, self).__init__(context, request)

    def __call__(self):
        if self.request.form.get("submitted", False):
            return self.handle_submit(REQUEST=self.request)
        return self.template()

    def handle_submit(self, REQUEST=None):
        pdf = self.request.get("pdf")
        data = "".join([x for x in pdf.xreadlines()])
        return self.download(data)

    def download(self, data, filename, mime_type="application/pdf"):
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=report.pdf")
        self.request.response.setHeader("Content-Type", mime_type)
        self.request.response.setHeader("Content-Length", len(data))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(data)
