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

import logging
import mimetypes
import os
import time
from string import Template

import bs4
from plone.subrequest import subrequest
from bika.lims import api
from senaite.impress import logger
from senaite.impress.decorators import synchronized
from senaite.impress.interfaces import IPublisher
from weasyprint import CSS
from weasyprint import HTML
from weasyprint import default_url_fetcher
from weasyprint.compat import base64_encode
from zope.interface import implements

IMG_TAG_TEMPLATE = Template("""<!-- PNG Report Page -->
<div class="report">
  <img src="${data}" style="width:${width}px; height:${height}px;"/>
</div>
""")


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

    def to_html(self, html):
        """Return plain HTML
        """
        if isinstance(html, bs4.Tag):
            return html.prettify()
        if isinstance(html, basestring):
            return html
        raise TypeError("Unknown HTML type {}".format(type(html)))

    def get_parser(self, html, parser="html.parser"):
        """Returns a HTML parser instance
        """
        return bs4.BeautifulSoup(html, parser)

    def parse_reports(self, html):
        """Parse reports from the given html

        :returns: List of report nodes
        """
        parser = self.get_parser(html)
        reports = parser.find_all(
            "div", class_=self.css_class_report)
        return reports

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
        # ensure we have plain html and not a BS4 node
        html = self.to_html(html)

        start = time.time()
        # Lay out and paginate the document
        html = HTML(
            string=html, url_fetcher=self.url_fetcher, base_url=self.base_url)
        document = html.render(stylesheets=self.css)
        end = time.time()
        logger.info("Publisher::Layout step took {:.2f}s for {} pages"
                    .format(end-start, len(document.pages)))
        return document

    @synchronized(max_connections=2)
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

    def write_png(self, html, resolution=96):
        """Write a PNG from the given HTML
        """
        doc = self._layout_and_paginate(html)
        return doc.write_png(resultion=resolution)

    def write_pdf(self, html):
        """Write a PDF from the given HTML
        """
        doc = self._layout_and_paginate(html)
        return doc.write_pdf()

    def write_png_pages(self, html, resolution=96):
        """Write one PNG per page from the given HTML

        :returns: List of (png_bytes, width, height) tuples per page
        """
        doc = self._layout_and_paginate(html)

        pages = []
        for i, page in enumerate(doc.pages):
            # Render page to PNG
            png_bytes, width, height = doc.copy([page]).write_png(
                resolution=resolution)
            # Append tuple of (png_bytes, width, height)
            pages.append((png_bytes, width, height))
        return pages

    def png_to_img(self, png, width, height, **kw):
        """Generate a data url image tag
        """
        data_url = "data:image/png;base64," + (
            base64_encode(png).decode("ascii").replace("\n", ""))
        img = IMG_TAG_TEMPLATE.safe_substitute(
            width=width, height=height, data=data_url, **kw)
        return img
