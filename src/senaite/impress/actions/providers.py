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

import collections
from datetime import datetime

import six

from bika.lims import api
from bika.lims.api import mail as mailapi
from bika.lims.interfaces import IAnalysisRequest
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.impress import senaiteMessageFactory as _


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
        self.objects = map(api.get_object, self.uids)
        self.action_url = "{}/{}".format(api.get_url(context), self.__name__)

    def __call__(self):
        if self.request.form.get("submitted", False):
            self.send(REQUEST=self.request)
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

    def is_sample(self, obj):
        """Check if the given object is a sample
        """
        return IAnalysisRequest.providedBy(obj)

    def get_email_sender_address(self):
        """Sender email is either the lab email or portal email "from" address
        """
        lab_email = self.laboratory.getEmailAddress()
        portal_email = api.get_registry_record("plone.email_from_address")
        return lab_email or portal_email or ""

    def get_default_recipient_emails(self):
        """Return the default recipient emails
        """
        emails = []
        for obj in self.objects:
            if not self.is_sample(obj):
                continue
            contact = obj.getContact()
            if not contact:
                continue
            email = contact.getEmailAddress()
            if email not in emails:
                emails.append(email)
        return ", ".join(filter(mailapi.is_valid_email_address, emails))

    def get_default_cc_emails(self):
        """Return the default CC emails
        """
        emails = []
        for obj in self.objects:
            if not self.is_sample(obj):
                continue
            for contact in obj.getCCContact():
                if not contact:
                    continue
                email = contact.getEmailAddress()
                if email not in emails:
                    emails.append(email)
            for email in obj.getCCEmails().split(","):
                if email not in emails:
                    emails.append(email)
        return ", ".join(filter(mailapi.is_valid_email_address, emails))

    def get_default_subject(self):
        """Return the default subject
        """
        return ", ".join(map(api.get_id, self.objects))

    def get_default_body(self):
        """Return the default body text
        """
        return ""

    def get_default_pdf_filename(self):
        """Return the default filename of the attached PDF
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        return "Report-{}.pdf".format(timestamp)

    def send(self, REQUEST=None):
        email_to = self.request.get("email_to", "")
        email_cc = self.request.get("email_cc", "")
        email_subject = self.request.get("email_subject", "")
        email_body = self.request.get("email_body", "")

        pdf = self.request.get("pdf")
        if not pdf:
            message = _("PDF attachment is missing")
            self.add_status_message(message, level="error")
            return False

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
            message = _("Failed to send Email")
            self.add_status_message(message, level="error")
            return False

        message = _("Email sent")
        self.add_status_message(message, level="info")
        return True
