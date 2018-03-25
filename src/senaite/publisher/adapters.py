# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import json
import logging
import mimetypes
import os
import time

from bs4 import BeautifulSoup
from DateTime import DateTime
from plone.subrequest import subrequest
from Products.ZCatalog.Lazy import LazyMap
from senaite import api
from senaite.publisher import logger
from senaite.publisher.decorators import synchronized
from senaite.publisher.interfaces import (IPublicationObject, IPublisher,
                                          ITemplateOptionsProvider)
from weasyprint import CSS, HTML, default_url_fetcher
from weasyprint.compat import base64_encode
from zope.component import queryAdapter
from zope.interface import implements


class Publisher(object):
    """Publishes HTML into printable formats
    """
    implements(IPublisher)

    css_class_report = "report"
    css_class_header = "section-header"
    css_class_footer = "section-footer"
    css_resources = "++resource++senaite.publisher.static/css"

    def __init__(self, html):
        # Ignore WeasyPrint warnings for unknown CSS properties
        logging.getLogger('weasyprint').setLevel(logging.ERROR)
        self.html = html
        self.css = []

    def link_css_file(self, css_file):
        """Link a CSS file
        """
        css = os.path.basename(css_file)
        path = "{}/{}/{}".format(self.base_url, self.css_resources, css)
        if path not in self.css:
            self.css.append(path)

    def add_inline_css(self, css):
        """Add an inline CSS
        """
        self.css.append(CSS(string=css))

    @property
    def base_url(self):
        """Portal Base URL
        """
        return api.get_portal().absolute_url()

    def get_parser(self, html, parser="html.parser"):
        """Returns a HTML parser instance
        """
        return BeautifulSoup(html, parser)

    def get_reports(self):
        """Returns a list of parsed reports
        """
        parser = self.get_parser(self.html)
        reports = parser.find_all("div", class_=self.css_class_report)
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
        html = HTML(string=html, url_fetcher=self.url_fetcher,
                    base_url=self.base_url)
        document = html.render(stylesheets=self.css)
        end = time.time()
        logger.info("Publisher::Layout step took {:.2f}s for {} pages"
                    .format(end-start, len(document.pages)))
        return document

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

    def write_png(self, merge=False):
        """Write PNGs from the given HTML
        """
        pages = []
        reports = self.get_reports()
        if merge:
            reports = ["".join(reports)]

        for report in reports:
            document = self._layout_and_paginate(report)
            for i, page in enumerate(document.pages):
                # Render page to PNG
                # What is the default DPI of the browser print dialog?
                png_bytes, width, height = document.copy([page]).write_png(
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

    def write_pdf(self, merge=False):
        """Write PDFs from the given HTML
        """
        reports = self.get_reports()
        if merge:
            reports = ["".join(reports)]

        pages = []
        main_document = None
        for n, report in enumerate(reports):
            document = self._layout_and_paginate(report)
            if n == 0:
                main_document = document
            pages.extend(document.pages)

        # Render page to PDF
        pdf = main_document.copy(pages).write_pdf()
        return pdf


class TemplateOptionsProvider(object):
    """Provides options which can be passed into oage templates as keywords

    In Zope Page Templates the keywords are then available in `options`:
    https://docs.zope.org/zope2/zope2book/AppendixC.html#built-in-names
    """
    implements(ITemplateOptionsProvider)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def options(self):
        """Template options dictionary
        """

        portal = api.get_portal()
        setup = portal.bika_setup
        laboratory = setup.laboratory

        # Note: We wrap objects to Publication Objects to have a dictionary
        #       like access to the provided fields and methods
        return {
            "portal": PublicationObject("0"),
            "setup": PublicationObject(api.get_uid(setup)),
            "laboratory": PublicationObject(api.get_uid(laboratory)),
        }


class PublicationObject(object):
    """Publication Content Wrapper

    This wrapper exposes the schema fields of the wrapped content object as
    attributes. The schema field values are looked up by their accessors.

    If the primary catalog of the wrapped object contains a metadata column
    with the same name as the accessor, the metadata colum value is used
    instead.

    Note: Adapter lookup is done by `portal_type` name, e.g.:

    >>> portal_type = api.get_portal_type(self.context)
    >>> adapter = queryAdapter(uid, IPublicationObject, name=portal_type)
    """
    implements(IPublicationObject)

    def __init__(self, uid):
        logger.debug("PublicationObject({})".format(uid))

        self._uid = uid
        self._brain = None
        self._catalog = None
        self._instance = None

        self.__empty_marker = object
        self.data = dict()

    def __repr__(self):
        return "<{}:UID({})>".format(
            self.__class__.__name__, self.uid)

    def __str__(self):
        return self.uid

    def __hash__(self):
        return hash(self.uid)

    def __getitem__(self, key):
        value = self.get(key, self.__empty_marker)
        if value is not self.__empty_marker:
            return value
        raise KeyError(key)

    def __getattr__(self, name):
        value = self.get(name, self.__empty_marker)
        if value is not self.__empty_marker:
            return value
        # tab completion in pdbpp
        if name == "__members__":
            return self.keys()
        raise AttributeError(name)

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        return self.instance.Schema().keys()

    def iteritems(self):
        for k in self:
            yield (k, self[k])

    def iterkeys(self):
        return self.__iter__()

    def values(self):
        return [v for _, v in self.iteritems()]

    def items(self):
        return list(self.iteritems())

    def get_field(self, name, default=None):
        accessor = getattr(self.instance, "getField", None)
        if accessor is None:
            return default
        return accessor(name)

    def get(self, name, default=None):
        # Internal lookup in the data dict
        value = self.data.get(name, self.__empty_marker)
        if value is not self.__empty_marker:
            return self.data[name]

        # Field lookup on the instance
        field = self.get_field(name)
        if field is None:
            # expose non-private members of the instance to have access to e.g.
            # self.absolute_url()
            if not name.startswith("_") or not name.startswith("__"):
                return getattr(self.instance, name, default)
            return default

        # Retrieve field value by accessor
        accessor = field.getAccessor(self.instance)
        accessor_name = accessor.__name__

        # Metadata lookup by accessor name
        value = getattr(self.brain, accessor_name, self.__empty_marker)
        if value is self.__empty_marker:
            logger.debug("Add metadata column '{}' to the catalog '{}' "
                         "to increase performance!"
                         .format(accessor_name, self.catalog.__name__))
            value = accessor()

        # Process value for publication
        value = self.process_value(value)

        # Store value in the internal data dict
        self.data[name] = value

        return value

    def process_value(self, value):
        """Process publication value
        """
        # UID -> PublicationObject
        if self.is_uid(value):
            return self.get_publish_adapter_for_uid(value)
        # Content -> PublicationObject
        elif api.is_object(value):
            return self.get_publish_adapter_for_uid(api.get_uid(value))
        # DateTime -> DateTime
        elif isinstance(value, DateTime):
            return value
        # Process list values
        elif isinstance(value, (LazyMap, list, tuple)):
            return map(self.process_value, value)
        # Process dict values
        elif isinstance(value, (dict)):
            return {k: self.process_value(v) for k, v in value.iteritems()}
        # Process function
        elif callable(value):
            return self.process_value(value())
        # Always return the unprocessed value last
        return value

    @property
    def uid(self):
        """UID of the wrapped object
        """
        return self._uid

    @property
    def instance(self):
        """Content instance of the wrapped object
        """
        if self._instance is None:
            logger.debug("PublicationObject::instance: *Wakup object*")
            self._instance = api.get_object(self.brain)
        return self._instance

    @property
    def brain(self):
        """Catalog brain of the wrapped object
        """
        if self._brain is None:
            logger.debug("PublicationObject::brain: *Fetch catalog brain*")
            self._brain = self.get_brain_by_uid(self.uid)
            # refetch the brain with the correct catalog
            results = self.catalog({"UID": self.uid})
            if results and len(results) == 1:
                self._brain = results[0]
        return self._brain

    @property
    def catalog(self):
        """Primary registered catalog for the wrapped portal type
        """
        if self._catalog is None:
            logger.debug("PublicationObject::catalog: *Fetch catalog*")
            archetype_tool = api.get_tool("archetype_tool")
            portal_type = self.brain.portal_type
            catalogs = archetype_tool.getCatalogsByType(portal_type)
            if catalogs is None:
                logger.warn("No registered catalog found for portal_type={}"
                            .format(portal_type))
                return api.get_tool("uid_catalog")
            self._catalog = catalogs[0]
        return self._catalog

    @property
    def workflows(self):
        """Return a list of assigned workflows
        """
        wf_ids = api.get_workflows_for(self.instance)
        return map(self.get_workflow_info_for, wf_ids)

    def get_workflow_info_for(self, wf_id):
        """Return a workflow info object
        """
        wf_tool = api.get_tool("portal_workflow")
        # `DCWorkflowDefinition` instance
        workflow = wf_tool.getWorkflowById(wf_id)
        # the state variable, e.g. review_state
        state_var = workflow.state_var
        # tuple of possible transitions
        transitions = wf_tool.getTransitionsFor(self.instance)
        # review history tuple, e.g. ({'action': 'publish', ...}, )
        history = wf_tool.getHistoryOf(wf_id, self.instance)
        # reverse the history
        review_history = history[::-1]
        # the most current history info
        current_state = review_history[0]
        # extracted status id
        status = current_state[state_var]
        # `StateDefinition` instance
        state_definition = workflow.states[status]
        # status title, e.g. "Published"
        status_title = state_definition.title

        # return selected workflow information for the wrapped instance
        return {
            "id": wf_id,
            "status": status,
            "status_title": status_title,
            "state_var": state_var,
            "transitions": transitions,
            "review_history": review_history,
        }

    def get_brain_by_uid(self, uid):
        """Lookup brain in the UID catalog
        """
        if uid == "0":
            return api.get_portal()
        uid_catalog = api.get_tool("uid_catalog")
        results = uid_catalog({"UID": uid})
        if len(results) != 1:
            raise ValueError("Failed to get brain by UID")
        return results[0]

    def get_publish_adapter_for_uid(self, uid):
        """Return a IPublicationObject adapter for the given UID
        """
        brain = self.get_brain_by_uid(uid)
        portal_type = brain.portal_type
        adapter = queryAdapter(uid, IPublicationObject, name=portal_type)
        if adapter is None:
            return PublicationObject(uid)
        return adapter

    def is_valid(self):
        """Self-check
        """
        try:
            self.brain
        except ValueError:
            return False
        return True

    def is_uid(self, uid):
        """Check valid UID format
        """
        if not isinstance(uid, basestring):
            return False
        if len(uid) != 32:
            return False
        if not uid.isalnum():
            return False
        return True

    def stringify(self, value):
        """Convert value to string
        """
        # PublicationObject -> UID
        if IPublicationObject.providedBy(value):
            return str(value)
        # DateTime -> ISO8601 format
        elif isinstance(value, (DateTime)):
            return value.ISO8601()
        # Dict -> convert_value_to_string
        elif isinstance(value, dict):
            return {k: self.stringify(v) for k, v in value.iteritems()}
        # List -> convert_value_to_string
        if isinstance(value, (list, tuple, LazyMap)):
            return map(self.stringify, value)
        return str(value)

    def to_dict(self, converter=None):
        """Returns a copy dict of the current object

        If a converter function is given, pass each value to it.
        Per default the values are converted by `self.stringify`.
        """
        if converter is None:
            converter = self.stringify
        out = dict()
        for k, v in self.iteritems():
            out[k] = converter(v)
        return out

    def to_json(self):
        """Returns a JSON representation of the current object
        """
        return json.dumps(self.to_dict())
