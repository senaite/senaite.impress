# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

from string import Template

from senaite import api
from senaite.publisher import logger
from senaite.publisher.decorators import returns_report_model
from senaite.publisher.interfaces import IMultiReportView
from senaite.publisher.interfaces import IReportView
from zope.component import getAdapter
from zope.globalrequest import getRequest
from zope.interface import implements


TEMPLATE = Template("""<!-- Multi Report Template -->
<div class="report">
  <script type="text/javascript">
    console.log("*** BEFORE MULTI TEMPLATE RENDER ***");
  </script>
  ${template}
</div>
""")


class MultiReportView(object):
    implements(IMultiReportView)

    def __init__(self, collection):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        self.collection = collection
        self.request = getRequest()

        # needed for template rendering
        self.context = self.portal

    def render(self, template):
        context = self.get_template_context(self.collection)
        template = Template(template).safe_substitute(context)
        return TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, collection):
        return {}

    def get_reportview_for(self, model):
        view = getAdapter(model, IReportView, name="AnalysisRequest")
        return view

    @property
    @returns_report_model
    def portal(self):
        return api.get_portal()

    @property
    @returns_report_model
    def setup(self):
        return self.portal.bika_setup

    @property
    @returns_report_model
    def laboratory(self):
        return self.setup.laboratory

    @property
    def current_user(self):
        user = api.get_current_user()
        return api.get_user_properties(user)
