# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import os
from collections import defaultdict
from string import Template

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
from senaite.impress import logger
from senaite.impress.config import PAPERFORMATS
from senaite.impress.interfaces import IMultiReportView
from senaite.impress.interfaces import IPublisher
from senaite.impress.interfaces import IPublishView
from senaite.impress.interfaces import IReportModel
from senaite.impress.interfaces import IReportView
from senaite.impress.interfaces import ITemplateFinder
from zope.component import ComponentLookupError
from zope.component import getAdapter
from zope.component import getUtility
from zope.interface import implements


CSS = Template("""/** Paper Format CSS **/
@page {
  /* width/height according to the format */
  size: ${page_width}mm ${page_height}mm;

  /* margins on every page */
  margin-top: ${margin_top}mm;
  margin-right: ${margin_right}mm;
  margin-bottom: ${margin_bottom}mm;
  margin-left: ${margin_left}mm;
}
@media print {
  .report {
    /* width/height with subtracted margins */
    width: ${content_width}mm;
    height: ${content_height}mm;
  }
}
@media screen {
  .report {
    /* full width/height in preview only */
    width: ${page_width}mm;
    height: ${page_height}mm;
  }
  /* Bootstrap container fixture to display the full paper */
  @media (min-width: ${content_width}mm) {
    .container {
        min-width: ${page_width}mm!important;
    }
  }
}
""")


class PublishView(BrowserView):
    """Publish View Controller
    """
    implements(IPublishView)
    template = ViewPageTemplateFile("templates/publish.pt")

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()

    @property
    def portal(self):
        """Return the portal object
        """
        return api.get_portal()

    @property
    def user(self):
        return api.get_current_user()

    @property
    def publisher(self):
        """Provides a configured publisher instance
        """
        publisher = getUtility(IPublisher)
        # flush any linked CSS
        publisher.css = []
        # link default stylesheets
        publisher.link_css_file("bootstrap.min.css")
        publisher.link_css_file("print.css")
        return publisher

    def is_manager(self):
        """Checks if the current user has manager rights
        """
        from bika.lims.permissions import ManageBika
        roles = api.get_roles_for_permission(ManageBika, self.context)
        return self.user.has_role(roles)

    def is_publisher(self):
        """Checks if the current user has publisher rights
        """
        from bika.lims.permissions import Publish
        roles = api.get_roles_for_permission(Publish, self.context)
        return self.user.has_role(roles)

    def get_uids(self):
        """Parse the UIDs from the request `items` parameter
        """
        return filter(None, self.request.get("items", "").split(","))

    def get_collection(self, uids=None):
        """Wraps the given UIDs into a collection of ReportModels
        """
        if uids is None:
            uids = self.get_uids()
        collection = []
        for model in map(self.to_model, uids):
            if model.is_valid():
                collection.append(model)
            else:
                logger.error("Could not fetch report model for UID={}"
                             .format(model.uid))
        return collection

    def to_model(self, uid):
        """Returns a report Model for the given UID
        """
        model = None
        # Fetch the report (portal-) type for component lookups
        _type = self.get_report_type()
        try:
            model = getAdapter(uid, IReportModel, name=_type)
        except ComponentLookupError:
            logger.error("Lookup Error: No Report Model registered for name={}"
                         .format(_type))
            model = getAdapter(uid, IReportModel)

        logger.debug("Created Model for UID={}->{}".format(uid, model))
        return model

    def get_report_type(self):
        """Returns the (portal-) for the report
        """
        # We fall back to AnalysisRequest here, because this is the primary
        # report object we need at the moment.
        # However, we can later easy provide with this mechanism reports for
        # any other content type as well.
        return self.request.form.get("type", "AnalysisRequest")

    def render_reports(self, uids=None, **kw):
        """Render Single/Multi Reports to HTML
        """
        htmls = []
        template = self.get_report_template(kw.get("template"))
        collection = self.get_collection(uids)

        if self.is_multi_template(template):
            group = kw.get("group_by_client", True)

            # group the models by client
            if group:
                by_client = defaultdict(list)

                for model in collection:
                    by_client[model.Client.getId()].append(model)

                for client, collection in by_client.items():
                    # render multi report
                    html = self.render_multi_report(collection, template)
                    htmls.append(html)
            else:
                # render multi report
                html = self.render_multi_report(collection, template)
                htmls.append(html)
        else:
            for model in collection:
                # render single report
                html = self.render_report(model, template)
                htmls.append(html)

        return "\n".join(htmls)

    def render_report(self, model, template, **kw):
        """Render a ReportModel to HTML
        """
        _type = self.get_report_type()
        view = getAdapter(model, IReportView, name=_type)
        return view.render(self.read_template(template, view, **kw))

    def render_multi_report(self, collection, template, **kw):
        """Render multiple ReportModels to HTML
        """
        _type = self.get_report_type()
        view = getAdapter(collection, IMultiReportView, name=_type)
        return view.render(self.read_template(template, view, **kw))

    def get_print_css(self, paperformat="A4", orientation="portrait"):
        """Returns the generated print CSS for the given format/orientation
        """
        _paperformat = self.get_paperformat(paperformat)

        margin_top = _paperformat["margin_top"]
        margin_right = _paperformat["margin_right"]
        margin_bottom = _paperformat["margin_bottom"]
        margin_left = _paperformat["margin_left"]

        page_width = _paperformat["page_width"]
        page_height = _paperformat["page_height"]

        # calculate content width/height accordding to the margins
        content_height = page_height - margin_top - margin_bottom
        content_width = page_width - margin_left - margin_right

        _paperformat["content_width"] = content_width
        _paperformat["content_height"] = content_height

        # Flip sizes in landscape
        if orientation == "landscape":
            _paperformat["page_width"] = page_height
            _paperformat["page_height"] = page_width
            _paperformat["content_width"] = content_height
            _paperformat["content_height"] = content_width

        return CSS.safe_substitute(_paperformat)

    def get_paperformat(self, paperformat):
        """Return the paperformat dictionary
        """
        paperformats = self.get_paperformats()
        if paperformat not in paperformats:
            raise KeyError("Unknown Paper Format '{}'".format(paperformat))
        return paperformats[paperformat].copy()

    def get_paperformats(self):
        """Returns a mapping of available paper formats
        """
        # Todo: Implement cascading lookup: client->registry->config
        return PAPERFORMATS

    def get_report_templates(self, extensions=[".pt", ".html"]):
        """Returns a sorted list of template/path pairs
        """
        finder = getUtility(ITemplateFinder)
        templates = finder.get_templates(extensions=extensions)
        return sorted(map(lambda item: item[0], templates))

    def get_default_template(self, default="senaite.lims:Default.pt"):
        """Returns the configured default template from the registry
        """
        template = api.get_registry_record(
            "senaite.impress.default_template")
        if template is None:
            return default
        return template

    def get_default_paperformat(self, default="A4"):
        """Returns the configured default paperformat from the registry
        """
        paperformat = api.get_registry_record(
            "senaite.impress.default_paperformat")
        if paperformat is None:
            return default
        return paperformat

    def get_default_orientation(self, default="portrait"):
        """Returns the configured default orientation from the registry
        """
        orientation = api.get_registry_record(
            "senaite.impress.default_orientation")
        if orientation is None:
            return default
        return orientation

    def get_report_template(self, template=None):
        """Returns the path of report template
        """
        finder = getUtility(ITemplateFinder)
        if template is None:
            template = self.request.get("template")
        template_path = finder.find_template(template)
        if template_path is None:
            return finder.default_template
        return template_path

    def read_template(self, template, instance, **kw):
        if self.is_page_template(template):
            template = ViewPageTemplateFile(template, **kw)(instance)
        else:
            with open(template, "r") as template:
                template = template.read()
        return template

    def is_multi_template(self, template):
        if not os.path.exists(template):
            template = self.get_report_template(template)
        filename = os.path.basename(template)
        basename, ext = os.path.splitext(filename)
        if basename.lower().startswith("multi"):
            return True
        if basename.lower().endswith("multi"):
            return True
        return False

    def is_page_template(self, template):
        _, ext = os.path.splitext(template)
        if ext in [".pt", ".zpt"]:
            return True
        return False
