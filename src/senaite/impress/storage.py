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

from operator import methodcaller

import transaction
from bika.lims import api
from plone.namedfile.file import NamedBlobFile
from senaite.core.interfaces import IReportStoredHandler
from senaite.impress import logger
from senaite.impress.decorators import synchronized
from senaite.impress.interfaces import IPdfReportStorage
from zope.component import queryMultiAdapter
from zope.interface import implements


class PdfReportStorageAdapter(object):
    """Storage adapter for PDF reports
    """
    implements(IPdfReportStorage)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_primary_report(self, objs):
        """Get the primary report

        TODO: It would be better to provide a radio selection in the publish
        view to let the user select the primary report.

        Also see here: https://github.com/senaite/senaite.impress/issues/58
        """
        # sort the objects by created to have the most recent object first
        objs = sorted(objs, key=methodcaller("created"), reverse=True)
        return objs[0]

    def store(self, pdf, html, uids, metadata=None):
        """Store the PDF in the primary object

        A multi-report is stored once. It references all contained objects,
        so it shows up in the reports of each of them.

        :param pdf: generated PDF report (binary)
        :param html: report HTML (string)
        :param uids: UIDs of the objects contained in the PDF
        :param metadata: dict of metadata to store
        :returns: list with the created report
        """

        if metadata is None:
            metadata = {}

        # get the contained objects
        objs = map(api.get_object_by_uid, uids)
        primary = self.get_primary_report(objs)

        report = self.create_report(primary, pdf, html, uids, metadata)

        # Let the integrator react on the stored report, e.g. to transition
        # the samples it contains. Note this takes place before the commit
        # below on purpose, so the report and whatever the handler does end
        # up in the same transaction
        self.notify_stored([report])

        transaction.commit()

        return [report]

    def notify_stored(self, reports):
        """Hand the stored reports over to the `IReportStoredHandler` adapter

        Does nothing when no adapter is registered, so senaite.impress keeps
        working on its own.

        :param reports: the newly created report objects
        """
        if not reports:
            return

        handler = queryMultiAdapter(
            (self.context, self.request), IReportStoredHandler)
        if handler is None:
            logger.debug("No IReportStoredHandler registered for {}".format(
                repr(self.context)))
            return

        handler(reports)

    @synchronized(max_connections=1)
    def create_report(self, parent, pdf, html, uids, metadata):
        """Create a new report object

        NOTE: We limit the creation of reports to 1 to avoid conflict errors on
              simultaneous publication. The transaction is committed in the
              store() method.

        :param parent: parent object where to create the report inside
        :returns: ResultsReport
        """

        parent_id = api.get_id(parent)
        logger.info("Create Report for {} ...".format(parent_id))

        # Convert PDF binary data to NamedBlobFile
        pdf_filename = "{}.pdf".format(parent_id)
        pdf_blob = NamedBlobFile(
            data=pdf,
            filename=api.safe_unicode(pdf_filename),
            contentType="application/pdf"
        )

        # Create the report object
        # Field setters are called automatically by api.create(), including
        # UIDReferenceField.set() which creates backreferences via event
        # handler
        report = api.create(
            parent,
            "ResultsReport",
            sample=api.get_uid(parent),
            contained_samples=uids if uids else [],
            pdf=pdf_blob,
            metadata=metadata if metadata else {})

        logger.info("Create Report for {} [DONE]".format(parent_id))

        return report
