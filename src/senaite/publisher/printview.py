# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import inspect
from operator import itemgetter
from string import Template

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
from senaite.publisher import logger
from senaite.publisher.config import PAPERFORMATS
from senaite.publisher.decorators import returns_json
from senaite.publisher.interfaces import IPrintView
from senaite.publisher.interfaces import IPublisher
from senaite.publisher.interfaces import IReportView
from senaite.publisher.interfaces import ITemplateFinder
from senaite.publisher.reportmodel import ReportModel
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


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


class PrintView(BrowserView):
    """Print View
    """
    implements(IPrintView)
    template = ViewPageTemplateFile("templates/printview.pt")

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.uids = filter(None, self.request.get("items", "").split(","))
        self.reports = map(lambda uid: ReportModel(uid), self.uids)
        if self.request.form.get("submitted", False):
            return self.download()
        return self.template()

    def render_report(self, uid):
        context = ReportModel(uid)
        request = self.request
        report = getMultiAdapter((context, request), IReportView,
                                 name="reportview")
        template = self.request.get("template")
        if template:
            report.set_template(template)
        return report.render()

    @property
    def paperformat(self):
        paperformats = self.get_paperformats()
        format = self.request.form.get("format")
        if format not in paperformats:
            format = "A4"
        orientation = self.request.form.get("orientation", "portrait")
        paperformat = paperformats.get(format)
        paperformat.update({
            "orientation": orientation,
        })
        return paperformat

    @property
    def css(self):
        setup = api.get_portal().bika_setup
        footer = setup.getResultFooter()
        context = self.paperformat
        context.update({
            "footer": "{}".format(footer.replace("\r\n", "\A"))
        })
        return CSS.substitute(context)

    def download(self):
        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!
        html = self.request.form.get("html").decode("utf8")
        css = self.css

        publisher = IPublisher(html)
        publisher.link_css_file("bootstrap.min.css")
        # publisher.link_css_file("print.css")
        publisher.add_inline_css(css)
        merge = self.request.get("merge") in ["on", "true", "yes", "1"]

        logger.info("PDF CSS: {}".format(css))
        pdf = publisher.write_pdf(merge=merge)

        filename = "_".join(map(lambda r: r.id, self.reports))
        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=%s.pdf" % filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdf))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdf)

    def get_paperformats(self):
        """Returns a mapping of available paper formats
        """
        # Todo: Implement cascading lookup: client->registry->config
        return PAPERFORMATS

    def get_templates(self, extensions=[".pt", ".html"]):
        """Returns a sorted list of template/path pairs
        """
        finder = getUtility(ITemplateFinder)
        templates = finder.get_templates(extensions=extensions)
        return sorted(templates, key=itemgetter(0))


class ajaxPrintView(PrintView):
    """Print View with Ajax exposed methods
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ajaxPrintView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    @returns_json
    def __call__(self):
        """Dispatch the path to a method and return JSON.
        """
        if len(self.traverse_subpath) < 1:
            return {}

        # check if the method exists
        func_arg = self.traverse_subpath[0]
        func_name = "ajax_{}".format(func_arg)
        func = getattr(self, func_name, None)
        if func is None:
            return self.fail("Invalid function", status=400)

        # Additional provided path segments after the function name are handled
        # as positional arguments
        args = self.traverse_subpath[1:]

        # check mandatory arguments
        func_sig = inspect.getargspec(func)
        # positional arguments after `self` argument
        required_args = func_sig.args[1:]

        if len(args) < len(required_args):
            return self.fail("Wrong signature, please use '{}/{}'"
                             .format(func_arg, "/".join(required_args)), 400)
        return func(*args)

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result

    def pick(self, dct, *keys, **kw):
        """Returns a copy of the dictionary filtered to only have values for the
        whitelisted keys (or list of valid keys)

        >>> pick({"name": "moe", "age": 50, "userid": "moe1"}, "name", "age")
        {'age': 50, 'name': 'moe'}
        """
        copy = dict()
        keys = keys and keys or dct.keys()
        converter = kw.get("converter")

        for key in keys:
            if key in dct.keys():
                copy[key] = self.convert(dct[key], converter)
        return copy

    def convert(self, value, converter):
        """Converts a value with a given converter function.
        """
        if not callable(converter):
            return value
        return converter(value)

    def ajax_get(self, uid, *args, **kwargs):
        """Return the JSONified

        Any additional positional parameter in *args will pick only these keys
        from the returned dictionary.
        """
        logger.info("ajaxPrintView::ajax_get_uid:UID={} args={}"
                    .format(uid, args))

        wrapped = ReportModel(uid)
        if not wrapped.is_valid():
            return self.fail("No object found for UID '{}'"
                             .format(uid), status=404)

        def converter(value):
            return wrapped.stringify(value)

        return self.pick(wrapped, converter=converter, *args)

    def ajax_paperformats(self, *args):
        """Returns the paperformats

        Any additional positional parameter in *args will pick only these keys
        from the returned dictionary.
        """
        return self.pick(self.get_paperformats(), *args)

    def ajax_render_reports(self, *args):
        """Renders all reports and returns the html
        """
        reports = []
        uids = filter(None, self.request.get("items", "").split(","))
        for uid in uids:
            reports.append(self.render_report(uid))
        return reports

    def ajax_load_preview(self):
        """Recalculate the HTML of one rendered report after all the embedded
        JavaScripts modified the report on the client side.
        """
        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!
        html = self.request.form.get("html").decode("utf8")
        return html
        css = self.css

        publisher = IPublisher(html)
        publisher.link_css_file("bootstrap.min.css")
        publisher.link_css_file("print.css")
        publisher.add_inline_css(css)
        merge = self.request.get("merge") in ["on", "true", "yes", "1"]

        logger.info("Preview CSS: {}".format(css))
        images = publisher.write_png(merge=merge)

        preview = ""
        for image in images:
            preview += publisher.png_to_img(*image)
        preview += "<style type='text/css'>{}</style>".format(css)
        return preview
