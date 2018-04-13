# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

import json
import os
from collections import defaultdict
from datetime import datetime
from string import Template

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
# from senaite.publisher import logger
from senaite.publisher.config import PAPERFORMATS
from senaite.publisher.interfaces import IMultiReportView
from senaite.publisher.interfaces import IPublisher
from senaite.publisher.interfaces import IPublishView
from senaite.publisher.interfaces import IReportView
from senaite.publisher.interfaces import ITemplateFinder
from senaite.publisher.reportmodel import ReportModel
from senaite.publisher.reportmodelcollection import ReportModelCollection
from zope.component import getAdapter
from zope.component import getUtility
from zope.interface import implements


CSS = Template("""/** Paper size **/
@page {
  size: ${format} ${orientation};
  margin: 0;

  /* needed on every page */
  padding-top: ${margin_top}mm;
  padding-right: 0;
  padding-bottom: ${margin_bottom}mm;
  padding-left: 0;

  /* Paging */
  @bottom-right {
    content: counter(page) "/" counter(pages);
    margin-top: -${margin_top}mm;
    margin-right: ${margin_right}mm;
    font-size: 9pt;
  }

  /* Footer */
  @bottom-left {
    content: "${footer}";
    margin-top: -${margin_top}mm;
    margin-left: ${margin_left}mm;
    font-size: 9pt;
  }
}
.report.${format} {
  padding-left: ${margin_left}mm;
  padding-right: ${margin_right}mm;
}
.report.${format} {
  width: ${page_width}mm;
  height: ${page_height}mm;
}
.report.${format}.landscape {
  width: ${page_height}mm;
  height: ${page_width}mm;
}
@media print {
  .report.${format} { width: ${page_width}mm; }
  .report.${format}.landscape { width: ${page_height}mm; }
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
        if self.request.form.get("download", False):
            return self.download()
        return self.template()

    def download(self):
        """Generate PDF and send it fot download
        """
        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!

        form = self.request.form
        html = form.get("html", "")
        context = {
            "format": form.get("format"),
            "orientation": form.get("orientation"),
            "template": form.get("template"),
        }

        publisher = self.get_publisher(html, **context)
        merge = json.loads(form.get("merge", "false"))
        pdf = publisher.write_pdf(merge=merge, uid=form.get("uid"))

        filename = "report_%s" % datetime.now().isoformat()
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=%s.pdf" % filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdf))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdf)

    def get_uids(self):
        """Parse the UIDs from the request `items` parameter
        """
        return filter(None, self.request.get("items", "").split(","))

    def get_collection(self, uids=None):
        """Wraps the given UIDs into a collection of ReportModels
        """
        if uids is None:
            uids = self.get_uids()
        models = map(lambda uid: ReportModel(uid), uids)
        return ReportModelCollection(models)

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
                by_client = defaultdict(ReportModelCollection)

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

    def render_report(self, model, template):
        """Render a ReportModel to HTML
        """
        view = getAdapter(model, IReportView, name="AnalysisRequest")
        return view.render(self.read_template(template, view))

    def render_multi_report(self, collection, template):
        """Render multiple ReportModels to HTML
        """
        view = getAdapter(collection, IMultiReportView, name="AnalysisRequest")
        return view.render(self.read_template(template, view))

    def get_publisher(self, html, **kw):
        """Returns a configured IPublisher instance
        """
        publisher = IPublisher(html)

        # generate print CSS
        css = self.get_print_css(**kw)

        # link CSS
        publisher.link_css_file("bootstrap.min.css")
        publisher.link_css_file("print.css")
        publisher.add_inline_css(css)

        return publisher

    def get_print_css(self, **kw):
        """Returns the generated print CSS for the given format/orientation
        """
        format = kw.get("format", "A4")
        orientation = kw.get("orientation", "portrait")

        context = self.get_paperformat(format, orientation)
        context["footer"] = self.get_footer_text()
        return CSS.safe_substitute(context)

    def get_paperformat(self, format="A4", orientation="portrait"):
        paperformats = self.get_paperformats()
        if format not in paperformats:
            format = "A4"
        if orientation not in ["portrait", "landscape"]:
            orientation = "portrait"
        paperformat = paperformats.get(format)
        paperformat["orientation"] = orientation
        return paperformat

    def get_paperformats(self):
        """Returns a mapping of available paper formats
        """
        # Todo: Implement cascading lookup: client->registry->config
        return PAPERFORMATS

    def get_footer_text(self, escape=True):
        """Returns the footer text from the setup
        """
        setup = api.get_portal().bika_setup
        footer = setup.getResultFooter().decode("utf-8")
        if escape:
            return footer.replace("\r\n", "\A")
        return footer

    def get_report_templates(self, extensions=[".pt", ".html"]):
        """Returns a sorted list of template/path pairs
        """
        finder = getUtility(ITemplateFinder)
        templates = finder.get_templates(extensions=extensions)
        return sorted(map(lambda item: item[0], templates))

    def get_default_template(self):
        """Returns the configured default template from the registry
        """
        return api.get_registry_record("senaite.publisher.default_template")

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

    def read_template(self, template, instance):
        if self.is_page_template(template):
            template = ViewPageTemplateFile(template)(instance)
        else:
            with open(template, "r") as template:
                template = template.read()
        return template

    def is_multi_template(self, template):
        filename = os.path.basename(template)
        basename, ext = os.path.splitext(filename)
        if basename.lower().startswith("multi"):
            return True
        return False

    def is_page_template(self, template):
        _, ext = os.path.splitext(template)
        if ext in [".pt", ".zpt"]:
            return True
        return False
