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

import os
from collections import Iterable
from collections import OrderedDict
from functools import reduce
from string import Template

from bika.lims import api
from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.resource.utils import iterDirectoriesOfType
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.core.supermodel.interfaces import ISuperModel
from senaite.impress import logger
from senaite.impress.config import PAPERFORMATS
from senaite.impress.interfaces import IMultiReportView
from senaite.impress.interfaces import IPublisher
from senaite.impress.interfaces import IPublishView
from senaite.impress.interfaces import IReportView
from senaite.impress.interfaces import ITemplateFinder
from zope.component import ComponentLookupError
from zope.component import getAdapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
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
        if self.request.form.get("download", False):
            return self.download()
        return self.template()

    def download(self):
        """Generate PDF and send it fot download
        """
        form = self.request.form
        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # NOTE: It might also contain multiple reports!
        html = form.get("html", "")
        # convert to unicode
        # https://github.com/senaite/senaite.impress/pull/93
        html = api.safe_unicode(html)
        # get the selected template
        template = form.get("template")
        # get the selected paperformat
        paperformat = form.get("format")
        # get the selected orientation
        orientation = form.get("orientation", "portrait")
        # get the filename
        filename = form.get("filename", "{}.pdf".format(template))
        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Print CSS: {}".format(css))
        # get the publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)
        # generate the PDF
        pdf = publisher.write_pdf(html)

        self.request.response.setHeader(
            "Content-Disposition", "attachment; filename=%s.pdf" % filename)
        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Length", len(pdf))
        self.request.response.setHeader("Cache-Control", "no-store")
        self.request.response.setHeader("Pragma", "no-cache")
        self.request.response.write(pdf)

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
        publisher.link_css_file("bootstrap-print.css")
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
        return filter(api.is_uid, self.request.get("items", "").split(","))

    def get_request_parameter(self, parameter, default=None):
        """Returns the request parameter
        """
        return self.request.get(parameter, default)

    def get_collection(self, uids, group_by=None):
        """Wraps the given UIDs into a collection of SuperModels

        :param uids: list of UIDs
        :param group_by: Grouping field accessor, e.g getClientUID
        :returns: list of SuperModels
        """
        collection = []

        # filter out all non-UIDs
        uids = filter(api.is_uid, uids)

        for model in map(self.to_model, uids):
            if model.is_valid():
                collection.append(model)
            else:
                logger.error("Could not fetch report model for UID={}"
                             .format(model.uid))
        if group_by is not None:
            grouped_collection = self.group_items_by(group_by, collection)
            return reduce(lambda a, b: a+b, grouped_collection.values(), [])
        return collection

    def to_model(self, uid):
        """Returns a SuperModel for the given UID
        """
        model = None
        # Fetch the report (portal-) type for component lookups
        _type = self.get_report_type()
        try:
            model = getAdapter(uid, ISuperModel, name=_type)
        except ComponentLookupError:
            logger.error("Lookup Error: No SuperModel registered for name={}"
                         .format(_type))
            model = getAdapter(uid, ISuperModel)

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

    def get_report_view_controller(self, model_or_collection, interface):
        """Get a suitable report view controller

        Query the controller view as a multi-adapter to allow 3rd party
        overriding with a browser layer.
        """
        name = self.get_report_type()

        context = self.context
        request = self.request

        # Give precedence to multiadapters that adapt the context as well
        view = queryMultiAdapter(
            (context, model_or_collection, request), interface, name=name)
        if view is None:
            # Return the default multiadapter
            return getMultiAdapter(
                (model_or_collection, request), interface, name=name)
        return view

    def render_report(self, model, template, paperformat, orientation, **kw):
        """Render a SuperModel to HTML
        """
        # get the report view controller
        view = self.get_report_view_controller(model, IReportView)

        options = kw
        # pass through the calculated dimensions to the template
        options.update(self.calculate_dimensions(paperformat, orientation))
        template = self.read_template(template, view, **options)
        return view.render(template, **options)

    def render_multi_report(self, collection, template, paperformat, orientation, **kw):  # noqa
        """Render multiple SuperModels to HTML
        """
        # get the report view controller
        view = self.get_report_view_controller(collection, IMultiReportView)

        options = kw
        # pass through the calculated dimensions to the template
        options.update(self.calculate_dimensions(paperformat, orientation))

        template = self.read_template(template, view, **options)
        return view.render(template, **options)

    def calculate_dimensions(self, paperformat="A4", orientation="portrait"):
        """Calculate the page and content dimensions
        """
        pf = self.get_paperformat(paperformat)

        margin_top = pf["margin_top"]
        margin_right = pf["margin_right"]
        margin_bottom = pf["margin_bottom"]
        margin_left = pf["margin_left"]

        if orientation == "portrait":
            page_width = pf["page_width"]
            page_height = pf["page_height"]
        else:
            page_width = pf["page_height"]
            page_height = pf["page_width"]

        # calculate content width/height accordding to the margins
        content_width = page_width - margin_left - margin_right
        content_height = page_height - margin_top - margin_bottom

        # prepare the substitution context
        dimensions = pf.copy()
        dimensions.update({
            "page_width": page_width,
            "page_height": page_height,
            "content_width": content_width,
            "content_height": content_height,
            "orientation": orientation,
        })
        return dimensions

    def get_print_css(self, paperformat="A4", orientation="portrait"):
        """Returns the generated print CSS for the given format/orientation
        """
        dimensions = self.calculate_dimensions(
            paperformat=paperformat, orientation=orientation)
        return CSS.safe_substitute(dimensions)

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
        template = self.get_request_parameter("template")
        if self.template_exists(template):
            return template
        template = api.get_registry_record(
            "senaite.impress.default_template")
        if template is None:
            return default
        return template

    def get_default_paperformat(self, default="A4"):
        """Returns the configured default paperformat from the registry
        """
        paperformat = self.get_request_parameter("paperformat")
        if paperformat in self.get_paperformats():
            return paperformat
        paperformat = api.get_registry_record(
            "senaite.impress.default_paperformat")
        if paperformat is None:
            return default
        return paperformat

    def get_default_orientation(self, default="portrait"):
        """Returns the configured default orientation from the registry
        """
        orientation = self.get_request_parameter("orientation")
        if orientation in ["portrait", "landscape"]:
            return orientation
        orientation = api.get_registry_record(
            "senaite.impress.default_orientation")
        if orientation is None:
            return default
        return orientation

    def store_multireports_individually(self):
        """Returns the configured setting from the registry
        """
        store_individually = api.get_registry_record(
            "senaite.impress.store_multireports_individually")
        return store_individually

    def get_developer_mode(self):
        """Returns the configured setting from the registry
        """
        mode = api.get_registry_record(
            "senaite.impress.developer_mode", False)
        return mode

    def template_exists(self, template):
        """Checks if the template exists
        """
        if not template:
            return False
        finder = getUtility(ITemplateFinder)
        template_path = finder.find_template(template)
        if template_path is None:
            return False
        return True

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
            template = ViewPageTemplateFile(template)(instance, **kw)
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

    def group_items_by(self, key, items):
        """Group the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        results = OrderedDict()
        for item in items:
            group_key = item.get(key)
            if callable(group_key):
                group_key = group_key()
            if group_key in results:
                results[group_key].append(item)
            else:
                results[group_key] = [item]
        return results

    def get_language_info(self):
        """Returns the current configured languages
        """

        # Use the language selector viewlet
        viewlet = LanguageSelector(self.context, self.request, None, None)
        viewlet.update()

        return {
            "available": viewlet.available(),
            "languages": viewlet.languages(),
        }

    def get_custom_javascripts(self):
        """Load custom JavaScript resouces

        Example:

            <!-- senaite.impress JS resource directory -->
            <plone:static
                directory="js"
                type="senaite.impress.js"
                name="MY-CUSTOM-SCRIPTS"/>

        All JS files in this directory get rendered inline in the publishview
        """

        TYPE = "senaite.impress.js"

        scripts = []
        for resource in iterDirectoriesOfType(TYPE):
            for fname in resource.listDirectory():
                # only consider files
                if not resource.isFile(fname):
                    continue

                # only JS files
                if not os.path.splitext(fname)[-1] == ".js":
                    continue

                portal_url = self.portal.absolute_url()
                directory = resource.directory
                resourcename = resource.__name__

                scripts.append({
                    # XXX Seems like traversal does not work in Plone 4
                    "url": "{}/++{}++{}/{}".format(
                        portal_url, TYPE, resourcename, fname),
                    "directory": directory,
                    "filepath": os.path.join(directory, fname),
                    "filename": fname,
                    "resourcename": resourcename,
                    "filecontents": resource.readFile(fname),
                })

        return scripts
