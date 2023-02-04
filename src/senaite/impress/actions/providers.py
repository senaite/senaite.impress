# -*- coding: utf-8 -*-

import collections

import six

from bika.lims import api
from bika.lims.api import mail as mailapi
from senaite.impress.decorators import returns_json
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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


class SendPDF(CustomAction):
    """Email Action
    """
    template = ViewPageTemplateFile("templates/send_pdf.pt")

    def __init__(self, context, request):
        super(SendPDF, self).__init__(context, request)
        self.samples = map(api.get_object_by_uid, self.uids)

    def __call__(self):
        if self.request.form.get("submitted", False):
            self.handle_submit(REQUEST=self.request)
            return self.request.get_header("referer")
        return self.template()

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    @property
    def laboratory(self):
        """Laboratory object from the LIMS setup
        """
        return api.get_setup().laboratory

    def get_email_sender_address(self):
        """Sender email is either the lab email or portal email "from" address
        """
        lab_email = self.laboratory.getEmailAddress()
        portal_email = api.get_registry_record("plone.email_from_address")
        return lab_email or portal_email or ""

    @returns_json
    def handle_submit(self, REQUEST=None):
        email_to = self.request.get("email_to", "")
        email_cc = self.request.get("email_cc", "")
        email_subject = self.request.get("email_subject", "")
        email_body = self.request.get("email_body", "")

        pdf = self.request.get("pdf")
        pdf_filename = self.request.get("pdf_filename")
        # workaround for ZPublisher.HTTPRequest.FileUpload object
        pdf_data = "".join(pdf.xreadlines())
        pdf_attachment = mailapi.to_email_attachment(pdf_data, pdf_filename)

        mime_msg = mailapi.compose_email(
            self.get_email_sender_address(),
            email_to,
            email_subject,
            email_body,
            [pdf_attachment])
        mime_msg["CC"] = mailapi.to_email_address(email_cc)

        sent = mailapi.send_email(mime_msg)
        if not sent:
            import pdb; pdb.set_trace()

    def get_contact_emails(self):
        """Extract all contact emails of the reports
        """
        emails = []
        for sample in self.samples:
            contact = sample.getContact()
            if not contact:
                continue
            email = contact.getEmailAddress()
            if email not in emails:
                emails.append(email)
        return ", ".join(filter(mailapi.is_valid_email_address, emails))

    def get_cccontact_emails(self):
        """Extract all the cc contact emails of the reports
        """
        emails = []
        for sample in self.samples:
            for contact in sample.getCCContact():
                if not contact:
                    continue
                email = contact.getEmailAddress()
                if email not in emails:
                    emails.append(email)
            for email in sample.getCCEmails().split(","):
                if email not in emails:
                    emails.append(email)
        return ", ".join(filter(mailapi.is_valid_email_address, emails))

    def get_subject(self):
        """Return the default subject
        """
        return ", ".join(map(api.get_id, self.samples))
