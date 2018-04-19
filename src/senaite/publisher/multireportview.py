# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

from string import Template

from senaite import api
from senaite.publisher import logger
from senaite.publisher.reportview import ReportView
from senaite.publisher.interfaces import IMultiReportView
from senaite.publisher.interfaces import IReportTool
from senaite.publisher.interfaces import IReportView
from zope.component import getAdapter
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implements


# Wrapper template to pass in additional data, e.g. for HTML based templates
WRAPPER_TEMPLATE = Template("""<!-- Multi Report Template -->
<div class="report">
  <script type="text/javascript">
    console.log("*** BEFORE MULTI TEMPLATE RENDER ***");
  </script>
  ${template}
</div>
""")


class MultiReportView(ReportView):
    implements(IMultiReportView)

    def __init__(self, collection):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        self.collection = collection
        self.request = getRequest()

        # needed for template rendering
        self.context = api.get_portal()

    def render(self, template):
        """Wrap the template and render
        """
        context = {}  # additional context before rendering
        template = Template(template).safe_substitute(context)
        return WRAPPER_TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, collection):
        return {}


class ARMultiReportView(MultiReportView):
    """AR specific Multi Report View
    """

    def get_report_tool(self, name):
        """Returns the report tool

        :returns: IReportTool
        """
        return getUtility(IReportTool, name="AnalysisRequest")

    def get_reportview_for(self, model):
        """Returns the report view for the given model

        :returns: IReportView
        """
        return getAdapter(model, IReportView, name="AnalysisRequest")
