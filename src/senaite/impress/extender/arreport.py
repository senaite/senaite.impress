# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims.browser.widgets import ReferenceWidget
from bika.lims.interfaces import IARReport
from senaite.impress import logger
from senaite.impress import senaiteMessageFactory as _
from senaite.impress.extender import ExtRecordField
from senaite.impress.extender import ExtUIDReferenceField
from senaite.impress.interfaces import ILayer
from zope.component import adapts
from zope.interface import implements


class ARReportSchemaExtender(object):
    """Extend Schema Fields for Clients
    """
    layer = ILayer
    implements(
        ISchemaExtender,
        IBrowserLayerAwareExtender,
        IOrderableSchemaExtender)
    adapts(IARReport)

    fields = [
        ExtUIDReferenceField(
            "ContainedAnalysisRequests",
            multiValued=True,
            allowed_types=("AnalysisRequest",),
            relationship="ARReportAnalysisRequest",
            widget=ReferenceWidget(
                label=_("Contained Analysis Requests"),
                render_own_label=False,
                size=20,
                description=_("Referenced Analysis Requests in the PDF"),
                visible={
                    "edit": "visible",
                    "view": "visible",
                    "add": "edit",
                },
                catalog_name="bika_catalog_analysisrequest_listing",
                base_query={},
                showOn=True,
                colModel=[
                    {
                        "columnName": "UID",
                        "hidden": True,
                    }, {
                        "columnName": "Title",
                        "label": "Title"
                    }, {
                        "columnName": "ClientTitle",
                        "label": "Client"
                    },
                ],
            ),
        ),

        ExtRecordField(
            "Metadata",
            multiValued=True,
            ),
    ]

    def __init__(self, context):
        logger.debug("ARReportSchemaExtender::__init__: context=%r" % context)
        self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
        """Change the order of the extended fields
        """
        return original


class ARReportSchemaModifier(object):
    """Rearrange Schema Fields
    """
    layer = ILayer
    implements(
        ISchemaModifier,
        IBrowserLayerAwareExtender)
    adapts(IARReport)

    def __init__(self, context):
        logger.debug("ARReportSchemaModifier::__init__: context=%r" % context)
        self.context = context

    def fiddle(self, schema):
        return schema
