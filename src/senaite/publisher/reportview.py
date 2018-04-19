# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

import json
from collections import OrderedDict
from string import Template

from bika.lims import POINTS_OF_CAPTURE
from Products.CMFPlone.i18nl10n import ulocalized_time
from senaite import api
from senaite.publisher.decorators import returns_report_model
from senaite.publisher.interfaces import IReportTool
from senaite.publisher.interfaces import IReportView
from zope.component import getUtility
from zope.globalrequest import getRequest
from zope.interface import implements


TEMPLATE = Template("""<!-- Report Template ${id} -->
<div class="report" id="${id}" uid="${uid}">
  <script type="text/javascript">
    console.log("*** BEFORE TEMPLATE RENDER ${id} ***");
  </script>
  ${template}
</div>
""")


class ReportView(object):
    """Generic Report View

    Note: This is also the base class for the Multi Report View
    """
    implements(IReportView)

    def __init__(self, model):
        self.model = model
        self.context = model.instance
        self.request = getRequest()

    def render(self, template):
        context = self.get_template_context(self.model)
        template = Template(template).safe_substitute(context)
        return TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, model):
        return {
            "id": model.getId(),
            "uid": model.UID(),
            # XXX temporary piggypack solution to handle DateTime objects right
            "user": json.dumps(model.stringify(self.current_user)),
            "api": {
                "report": self.get_api_url(model),
                "setup": self.get_api_url(self.setup),
                "laboratory": self.get_api_url(self.laboratory),
            }
        }

    def get_api_url(self, model):
        """Returns the API URL for the passed in object
        """
        info = {
            "uid": model.UID(),
            "endpoint": "ajax_printview",
            "action": "get",
            "base_url": self.portal.absolute_url(),
        }
        return "{base_url}/{endpoint}/{action}/{uid}".format(**info)

    def get_resource_url(self, name, prefix=""):
        """Return the full resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)

    @property
    @returns_report_model
    def portal(self):
        return api.get_portal()

    @property
    def portal_url(self):
        return api.get_portal().absolute_url()

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
        properties = {
            "username": user.getId()
        }
        properties.update(api.get_user_properties(user))
        return properties

    @property
    def wf_tool(self):
        return api.get_tool("portal_workflow")

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": self.model.instance,
            "request": self.request,
            "domain": "bika",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    def get_footer_text(self, escape=True):
        """Returns the footer text from the setup
        """
        setup = self.setup
        footer = setup.getResultFooter().decode("utf-8")
        if escape:
            return footer.replace("\r\n", "\A")
        return footer


class ARReportView(ReportView):
    """AR specific Report View
    """

    def get_report_tool(self):
        """Returns the report tool

        :returns: IReportTool
        """
        return getUtility(IReportTool, name="AnalysisRequest")

    @property
    def points_of_capture(self):
        items = POINTS_OF_CAPTURE.items()
        return OrderedDict(items)
