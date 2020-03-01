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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from operator import methodcaller

import transaction
from bika.lims import api
from senaite.impress import logger
from senaite.impress.decorators import synchronized
from senaite.impress.interfaces import IPdfReportStorage
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
        view to let the user select the primary report when the option
        "store_individually" is deselected.

        Also see here: https://github.com/senaite/senaite.impress/issues/58
        """
        # sort the objects by created to have the most recent object first
        objs = sorted(objs, key=methodcaller("created"), reverse=True)
        return objs[0]

    def store_multireports_individually(self):
        """Returns the configured setting from the registry
        """
        store_individually = api.get_registry_record(
            "senaite.impress.store_multireports_individually")
        return store_individually

    def store(self, pdf, html, uids, metadata=None):
        """Store the PDF

        :param pdf: generated PDF report (binary)
        :param html: report HTML (string)
        :param uids: UIDs of the objects contained in the PDF
        :param metadata: dict of metadata to store
        """

        if metadata is None:
            metadata = {}

        # get the contained objects
        objs = map(api.get_object_by_uid, uids)

        # handle primary object storage
        if not self.store_multireports_individually():
            # reduce the list to the primary object only
            objs = [self.get_primary_report(objs)]

        # generate the reports
        reports = []
        for obj in objs:
            report = self.create_report(obj, pdf, html, uids, metadata)
            reports.append(report)

        return reports

    @synchronized(max_connections=1)
    def create_report(self, parent, pdf, html, uids, metadata):
        """Create a new report object

        NOTE: We limit the creation of reports to 1 to avoid conflict errors on
              simultaneous publication.

        :param parent: parent object where to create the report inside
        :returns: ARReport
        """

        parent_id = api.get_id(parent)
        logger.info("Create Report for {} ...".format(parent_id))

        # Manually update the view on the database to avoid conflict errors
        parent._p_jar.sync()

        # Create the report object
        report = api.create(
            parent,
            "ARReport",
            AnalysisRequest=api.get_uid(parent),
            Pdf=pdf,
            Html=html,
            ContainedAnalysisRequests=uids,
            Metadata=metadata)

        # Commit the changes
        transaction.commit()

        logger.info("Create Report for {} [DONE]".format(parent_id))

        return report
