# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import socket
from collections import OrderedDict
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.Utils import formataddr
from smtplib import SMTPException
from string import Template

from bika.lims import logger
from bika.lims.utils import to_utf8
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
from senaite.impress import senaiteMessageFactory as _
from ZODB.POSException import POSKeyError


class EmailView(BrowserView):
    """Email Attachments View
    """
    template = ViewPageTemplateFile("templates/email.pt")
    email_template = ViewPageTemplateFile("templates/email_template.pt")

    def __init__(self, context, request):
        super(EmailView, self).__init__(context, request)
        # disable Plone's editable border
        request.set("disable_border", True)
        # remember context/request
        self.context = context
        self.request = request
        self.url = self.context.absolute_url()
        # the URL to redirect on abort or after send
        self.exit_url = "{}/{}".format(self.url, "reports_listing")
        # we need to transform the title to unicode, so that we can use it for
        self.client_name = safe_unicode(self.context.Title())
        self.email_body = self.context.translate(_(self.email_template(self)))
        # string interpolation later
        # N.B. We need to translate the raw string before interpolation
        subject = self.context.translate(_("Analysis Results for {}"))
        self.email_subject = subject.format(self.client_name)
        self.allow_send = True

    def __call__(self):
        request = self.request
        form = request.form

        submitted = form.get("submitted", False)
        send = form.get("send", False)
        abort = form.get("abort", False)

        if submitted and send:
            logger.info("*** SENDING EMAIL ***")

            # Parse used defined values from the request form
            recipients = form.get("recipients", [])
            responsibles = form.get("responsibles", [])
            subject = form.get("subject")
            body = form.get("body")
            reports = self.get_reports()

            # Merge recipiens and responsibles
            recipients = set(recipients + responsibles)

            # sanity checks
            if not recipients:
                message = _("No email recipients selected")
                self.add_status_message(message, "error")
            if not subject:
                message = _("Please add an email subject")
                self.add_status_message(message, "error")
            if not body:
                message = _("Please add an email text")
                self.add_status_message(message, "error")
            if not reports:
                message = _("No attachments")
                self.add_status_message(message, "error")

            success = False
            if all([recipients, subject, body, reports]):
                success = self.send_email(recipients=recipients,
                                          subject=subject,
                                          body=body,
                                          reports=reports)
            if success:
                # selected name, email pairs which received the email
                pairs = map(self.parse_email, recipients)
                send_to_names = map(lambda p: p[0], pairs)

                # set recipients to the reports
                for report in reports:
                    ar = report.getAnalysisRequest()
                    # publish the AR
                    self.publish(ar)

                    # Publish all linked ARs of this report
                    # N.B. `ContainedAnalysisRequests` is an extended field
                    field = report.getField("ContainedAnalysisRequests")
                    contained_ars = field.get(report) or []
                    for obj in contained_ars:
                        self.publish(obj)

                    # add new recipients to the AR Report
                    new_recipients = filter(
                        lambda r: r.get("Fullname") in send_to_names,
                        self.get_recipients(ar))
                    self.set_report_recipients(report, new_recipients)

                message = _(u"Message sent to {}"
                            .format(", ".join(send_to_names)))
                self.add_status_message(message, "info")
                return request.response.redirect(self.exit_url)
            else:
                message = _("Failed to send Email(s)")
                self.add_status_message(message, "error")

        if submitted and abort:
            logger.info("*** EMAIL ABORTED ***")
            message = _("Email aborted")
            self.add_status_message(message, "info")
            return request.response.redirect(self.exit_url)

        # get the selected ARReport objects
        report_objs = self.get_reports()

        # calculate the total size of all PDFs
        self.total_size = reduce(
            lambda x, y: x+y, map(self.get_filesize, report_objs), 0)
        if self.total_size > self.max_email_size:
            # don't allow to send oversized emails
            self.allow_send = False
            message = _("Total size of email exceeded {:.1f} MB ({:.2f} MB)"
                        .format(self.max_email_size / 1024,
                                self.total_size / 1024))
            self.add_status_message(message, "error")

        # prepare the data for the template
        self.reports = map(self.get_report_data, report_objs)
        self.recipients = self.get_recipients_data(report_objs)
        self.responsibles = self.get_responsibles_data(report_objs)

        # inform the user about invalid/inactive recipients
        if not all(map(lambda r: r.get("valid"), self.recipients)):
            message = _(
                "Not all contacts are equal for the selected Reports. "
                "Please manually select recipients for this email.")
            self.add_status_message(message, "warning")

        if not all(map(lambda r: r.get("active"), self.recipients)):
            message = _(
                "Not all contacts have the email publication preference set. "
                "Please manually select recipients for this email.")
            self.add_status_message(message, "warning")

        return self.template()

    def set_report_recipients(self, report, recipients):
        """Set recipients to the reports w/o overwriting the old ones

        :param reports: list of ARReports
        :param recipients: list of name,email strings
        """
        to_set = report.getRecipients()
        for recipient in recipients:
            if recipient not in to_set:
                to_set.append(recipient)
        report.setRecipients(to_set)

    def publish(self, ar):
        """Set status to prepublished/published/republished
        """
        wf = api.get_tool("portal_workflow")
        status = wf.getInfoFor(ar, "review_state")
        transitions = {"verified": "publish",
                       "published": "republish"}
        transition = transitions.get(status, "prepublish")
        logger.info("AR Transition: {} -> {}".format(status, transition))
        try:
            wf.doActionFor(ar, transition)
            return True
        except WorkflowException as e:
            logger.debug(e)
            return False

    def parse_email(self, email):
        """parse an email to an unicode name, email tuple
        """
        splitted = safe_unicode(email).split(",")
        if len(splitted) == 1:
            return (False, splitted[0])
        elif len(splitted) == 2:
            return (splitted[0], splitted[1])
        else:
            raise ValueError("Could not parse email '{}'".format(email))

    def send_email(self,
                   recipients=None,
                   subject=None,
                   body=None,
                   reports=None):
        """Prepare and send email to the recipients

        :param recipients: a list of email or name,email strings
        :param subject: the email subject
        :param body: the email body
        :param reports: list of report objects to attach
        :returns: True if all emails were sent, else false
        """

        recipient_pairs = map(self.parse_email, recipients)
        template_context = {
            "recipients": "\n".join(
                map(lambda p: formataddr(p), recipient_pairs))
        }

        body_template = Template(safe_unicode(body)).safe_substitute(
            **template_context)

        _preamble = "This is a multi-part message in MIME format.\n"
        _from = formataddr((self.email_from_name, self.email_from_address))
        _subject = Header(s=safe_unicode(subject), charset="utf8")
        _body = MIMEText(body_template, _subtype="plain", _charset="utf8")

        # Create the enclosing message
        mime_msg = MIMEMultipart()
        mime_msg.preamble = _preamble
        mime_msg["Subject"] = _subject
        mime_msg["From"] = _from
        mime_msg.attach(_body)

        # Attach the PDFs
        for report in reports:
            ar = report.getAnalysisRequest()
            filename = "{}.pdf".format(ar.getId())
            attachment = MIMEApplication(report.getPdf().data, _subtype="pdf")
            attachment.add_header("Content-Disposition",
                                  "attachment; filename=%s" % filename)
            mime_msg.attach(attachment)

        success = []
        # Send one email per recipient
        for pair in recipient_pairs:
            # N.B.: Headers are added additive, so we need to remove any
            #       existing "To" headers
            # No KeyError is raised if the key does not exist.
            # https://docs.python.org/2/library/email.message.html#email.message.Message.__delitem__
            del mime_msg["To"]
            # N.B. Use only the email address to avoid Postfix Error 550:
            # Recipient address rejected: User unknown in local recipient table
            # mime_msg["To"] = formataddr(pair)
            mime_msg["To"] = pair[1]
            msg_string = mime_msg.as_string()
            sent = self.send(msg_string)
            if not sent:
                logger.error("Could not send email to {}".format(pair))
            success.append(sent)

        if not all(success):
            return False
        return True

    def send(self, msg_string, immediate=True):
        """Send the email via the MailHost tool
        """
        try:
            mailhost = api.get_tool("MailHost")
            mailhost.send(msg_string, immediate=immediate)
        except SMTPException as e:
            logger.error(e)
            return False
        except socket.error as e:
            logger.error(e)
            return False
        return True

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_report_data(self, report):
        """Report data to be used in the template
        """
        ar = report.getAnalysisRequest()
        pdf = report.getPdf()
        filesize = "{} Kb".format(self.get_filesize(pdf))
        filename = "{}.pdf".format(ar.getId())
        return {
            "ar": ar,
            "pdf": pdf,
            "obj": report,
            "uid": api.get_uid(report),
            "filesize": filesize,
            "filename": filename,
        }

    def get_recipients_data(self, reports):
        """Recipients data to be used in the template
        """
        if not reports:
            return []

        recipients = []
        recipient_names = []

        for num, report in enumerate(reports):
            # get the linked AR of this ARReport
            ar = report.getAnalysisRequest()
            # recipient names of this report
            report_recipient_names = []
            for recipient in self.get_recipients(ar):
                active = "email" in recipient.get("PublicationModes", False)
                name = recipient.get("Fullname")
                email = recipient.get("EmailAddress")
                record = {
                    "name": name,
                    "email": email,
                    "active": active,
                    "valid": True,
                }
                if record not in recipients:
                    recipients.append(record)
                # remember the name of the recipient for this report
                report_recipient_names.append(name)
            recipient_names.append(report_recipient_names)

        # recipient names, which all of the reports have in common
        common_names = set(recipient_names[0]).intersection(*recipient_names)
        # mark recipients not in common
        for recipient in recipients:
            if recipient.get("name") not in common_names:
                recipient["valid"] = False
        return recipients

    def get_responsibles_data(self, reports):
        """Responsibles data to be used in the template
        """
        if not reports:
            return []

        recipients = []
        recipient_names = []

        for num, report in enumerate(reports):
            # get the linked AR of this ARReport
            ar = report.getAnalysisRequest()

            # recipient names of this report
            report_recipient_names = []
            responsibles = ar.getResponsible()
            for manager_id in responsibles.get("ids", []):
                responsible = responsibles["dict"][manager_id]
                name = responsible.get("name")
                email = responsible.get("email")
                record = {
                    "name": name,
                    "email": email,
                    "active": True,
                    "valid": True,
                }
                if record not in recipients:
                    recipients.append(record)
                # remember the name of the recipient for this report
                report_recipient_names.append(name)
            recipient_names.append(report_recipient_names)

        # recipient names, which all of the reports have in common
        common_names = set(recipient_names[0]).intersection(*recipient_names)
        # mark recipients not in common
        for recipient in recipients:
            if recipient.get("name") not in common_names:
                recipient["valid"] = False

        return recipients

    @property
    def portal(self):
        return api.get_portal()

    @property
    def laboratory(self):
        return api.get_setup().laboratory

    @property
    def email_from_address(self):
        """Portal email
        """
        lab_email = self.laboratory.getEmailAddress()
        portal_email = self.portal.email_from_address
        return lab_email or portal_email

    @property
    def email_from_name(self):
        """Portal email name
        """
        lab_from_name = self.laboratory.getName()
        portal_from_name = self.portal.email_from_name
        return lab_from_name or portal_from_name

    @property
    def max_email_size(self):
        """Return the max. allowed email size in KB
        """
        max_size = api.get_registry_record(
            "senaite.impress.max_email_size")
        if max_size < 0:
            return 0.0
        return max_size * 1024

    def get_reports(self):
        """Return the objects from the UIDs given in the request
        """
        # Create a mapping of source ARs for copy
        uids = self.request.form.get("uids", [])
        # handle 'uids' GET parameter coming from a redirect
        if isinstance(uids, basestring):
            uids = uids.split(",")
        unique_uids = OrderedDict().fromkeys(uids).keys()
        return map(self.get_object_by_uid, unique_uids)

    def get_object_by_uid(self, uid):
        """Get the object by UID
        """
        logger.debug("get_object_by_uid::UID={}".format(uid))
        obj = api.get_object_by_uid(uid, None)
        if obj is None:
            logger.warn("!! No object found for UID #{} !!")
        return obj

    def get_filesize(self, pdf):
        """Return the filesize of the PDF as a float
        """
        try:
            filesize = float(pdf.get_size())
            return float("%.2f" % (filesize / 1024))
        except (POSKeyError, TypeError):
            return 0.0

    def get_recipients(self, ar):
        """Return the AR recipients in the same format like the AR Report
        expects in the records field `Recipients`
        """
        plone_utils = api.get_tool("plone_utils")

        def is_email(email):
            if not plone_utils.validateSingleEmailAddress(email):
                return False
            return True

        def recipient_from_contact(contact):
            if not contact:
                return None
            email = contact.getEmailAddress()
            return {
                "UID": api.get_uid(contact),
                "Username": contact.getUsername(),
                "Fullname": to_utf8(contact.Title()),
                "EmailAddress": email,
                "PublicationModes": contact.getPublicationPreference(),
            }

        def recipient_from_email(email):
            if not is_email(email):
                return None
            return {
                "UID": "",
                "Username": "",
                "Fullname": email,
                "EmailAddress": email,
                "PublicationModes": ("email", "pdf",),
            }

        # Primary Contacts
        to = filter(None, [recipient_from_contact(ar.getContact())])
        # CC Contacts
        cc = filter(None, map(recipient_from_contact, ar.getCCContact()))
        # CC Emails
        cc_emails = map(lambda x: x.strip(), ar.getCCEmails().split(","))
        cc_emails = filter(None, map(recipient_from_email, cc_emails))

        return to + cc + cc_emails
