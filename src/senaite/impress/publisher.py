# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import logging
import mimetypes
import os
import time

from bs4 import BeautifulSoup
from plone.subrequest import subrequest
from senaite import api
from senaite.impress import logger
from senaite.impress.decorators import synchronized
from senaite.impress.interfaces import IPublisher
from weasyprint import CSS
from weasyprint import HTML
from weasyprint import default_url_fetcher
from weasyprint.compat import base64_encode
from zope.interface import implements


class Publisher(object):
    """Publishes HTML into printable formats
    """
    implements(IPublisher)

    css_class_report = "report"
    css_class_header = "section-header"
    css_class_footer = "section-footer"
    css_resources = "++resource++senaite.impress.static/css"

    def __init__(self):
        # Ignore WeasyPrint warnings for unknown CSS properties
        logging.getLogger('weasyprint').setLevel(logging.ERROR)
        self.css = []

    def link_css_file(self, css_file):
        """Link a CSS file
        """
        css_file = os.path.basename(css_file)
        path = "{}/{}/{}".format(self.base_url, self.css_resources, css_file)
        css = CSS(
            url=path, url_fetcher=self.url_fetcher, base_url=self.base_url)
        self.css.append(css)

    def add_inline_css(self, css):
        """Add an inline CSS
        """
        css = CSS(
            string=css, url_fetcher=self.url_fetcher, base_url=self.base_url)
        self.css.append(css)

    @property
    def base_url(self):
        """Portal Base URL
        """
        return api.get_portal().absolute_url()

    def get_parser(self, html, parser="html.parser"):
        """Returns a HTML parser instance
        """
        return BeautifulSoup(html, parser)

    def get_reports(self, html, attrs={}):
        """Returns a list of parsed reports
        """
        parser = self.get_parser(html)
        reports = parser.find_all(
            "div", class_=self.css_class_report, attrs=attrs)
        return map(lambda report: report.prettify(), reports)

    def parse_report_sections(self, report_html):
        """Returns a dictionary of {header, report, footer}
        """

        parser = self.get_parser(report_html)
        report = parser.find("div", class_=self.css_class_report)

        header = report.find("div", class_=self.css_class_header)
        if header is not None:
            header = header.extract()

        footer = report.find("div", class_=self.css_class_footer)
        if footer is not None:
            footer = footer.extract()

        return {
            "header": header.prettify(),
            "report": report.prettify(),
            "footer": footer.prettify(),
        }

    def _layout_and_paginate(self, html):
        """Layout and paginate the given HTML into WeasyPrint `Document` objects

        http://weasyprint.readthedocs.io/en/stable/api.html#python-api
        """
        start = time.time()
        # Lay out and paginate the document
        html = HTML(
            string=html, url_fetcher=self.url_fetcher, base_url=self.base_url)
        document = html.render(stylesheets=self.css)
        end = time.time()
        logger.info("Publisher::Layout step took {:.2f}s for {} pages"
                    .format(end-start, len(document.pages)))
        return document

    def _render_reports(self, html, merge=False, uid=None):
        """Render the reports to WeasyPrint documents
        """
        reports = []
        if uid is not None:
            reports = self.get_reports(attrs={"uid": uid})
        else:
            reports = self.get_reports(html)

        # merge all reports to one PDF
        if merge:
            reports = ["".join(reports)]

        return map(self._layout_and_paginate, reports)

    @synchronized
    def url_fetcher(self, url):
        """Fetches internal URLs by path and not via an external request.

        N.B. Multiple calls to this method might exhaust the available threads
             of the server, which causes a hanging instance.
        """
        if url.startswith("data"):
            logger.info("Data URL, delegate to default URL fetcher...")
            return default_url_fetcher(url)

        logger.info("Fetching URL '{}' for WeasyPrint".format(url))

        # get the pyhsical path from the URL
        request = api.get_request()
        host = request.get_header("HOST")
        path = "/".join(request.physicalPathFromURL(url))

        # fetch the object by sub-request
        portal = api.get_portal()
        context = portal.restrictedTraverse(path, None)

        if context is None or host not in url:
            logger.info("External URL, delegate to default URL fetcher...")
            return default_url_fetcher(url)

        logger.info("Local URL, fetching data by path '{}'".format(path))

        # get the data via an authenticated subrequest
        response = subrequest(path)

        # Prepare the return data as required by WeasyPrint
        string = response.getBody()
        filename = url.split("/")[-1]
        mime_type = mimetypes.guess_type(url)[0]
        redirected_url = url

        return {
            "string": string,
            "filename": filename,
            "mime_type": mime_type,
            "redirected_url": redirected_url,
        }

    def write_png(self, html, merge=False, uid=None):
        """Write PNGs from the given HTML
        """
        pages = []
        reports = self._render_reports(html, merge=merge, uid=uid)
        for report in reports:
            for i, page in enumerate(report.pages):
                # Render page to PNG
                # What is the default DPI of the browser print dialog?
                png_bytes, width, height = report.copy([page]).write_png(
                    resolution=96)
                # Append tuple of (png_bytes, width, height)
                pages.append((png_bytes, width, height))

        return pages

    def png_to_img(self, png, width, height):
        """Generate a data url image tag
        """
        data_url = 'data:image/png;base64,' + (
            base64_encode(png).decode('ascii').replace('\n', ''))
        img = """<div class='report'>
                    <img src='{2}' style='width: {0}px; height: {1}px'/>
                  </div>""".format(width, height, data_url)
        return img

    def write_pdf(self, html, merge=False, uid=None):
        """Write PDFs from the given HTML
        """
        reports = self._render_reports(html, merge=merge, uid=uid)
        return map(lambda doc: doc.write_pdf(), reports)
