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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

import inspect
import json
from collections import OrderedDict

from bika.lims import _
from bika.lims import api
from DateTime import DateTime
from senaite.app.supermodel import SuperModel
from senaite.impress import logger
from senaite.impress.decorators import returns_json
from senaite.impress.decorators import timeit
from senaite.impress.interfaces import ICustomActionProvider
from senaite.impress.interfaces import IPdfReportStorage
from senaite.impress.interfaces import IReportWrapper
from senaite.impress.publishview import PublishView
from zope.component import getAdapters
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class AjaxPublishView(PublishView):
    """Publish View with Ajax exposed methods
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(AjaxPublishView, self).__init__(context, request)
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

        try:
            return func(*args)
        except Exception as exc:
            self.request.response.setStatus(500)
            return {"error": str(exc)}

    def add_status_message(self, message, level="info"):
        """Set a portal status message
        """
        return self.context.plone_utils.addPortalMessage(message, level)

    def get_json(self):
        """Extracts the JSON from the request
        """
        body = self.request.get("BODY", "{}")
        return json.loads(body)

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result

    def pick(self, model, *keys):
        """Returns a dictionary filtered to only have model values for the
           whitelisted keys (or list of valid keys)

        >>> data = pick(model, "absolute_url", "UID")
        >>> len(data) == 2
        True
        >>> data["absolute_url"] == model.absolute_url()
        True
        >>> data["UID"] == model.UID()
        True
        """
        data = dict()
        marker = object()

        for key in keys:
            value = getattr(model, key, marker)
            if value is not marker:
                data[key] = model.stringify(value)
        return data

    def ajax_get(self, uid, *args, **kwargs):
        """Return the JSONified data from the wrapped object

        Any additional positional parameter in *args will pick only these keys
        from the returned dictionary.
        """
        logger.info("ajaxPrintView::ajax_get: {}{}"
                    .format(uid, "/".join(args)))

        model = SuperModel(uid)
        if not model.is_valid():
            return self.fail("No object found for UID '{}'"
                             .format(uid), status=404)

        if args:
            return self.pick(model, *args)
        return model.to_dict()

    def ajax_paperformats(self, *args):
        """Returns the paperformats

        Any additional positional parameter in *args will pick only these keys
        from the returned dictionary.
        """
        return self.get_paperformats()

    def ajax_templates(self):
        """Returns the available templates
        """
        return self.get_report_templates()

    def ajax_config(self):
        """Returns the default publisher config
        """
        custom_actions = []

        # Query custom action providers
        adapters = getAdapters(
            (self, self.context, self.request), ICustomActionProvider)
        for name, adapter in adapters:
            # skip the adapter if it is not available
            if not adapter.available():
                continue
            custom_actions.append(adapter.get_action_data())

        config = {
            "format": self.get_default_paperformat(),
            "orientation": self.get_default_orientation(),
            "template": self.get_default_template(),
            "reload_after_reorder": self.get_reload_after_reorder(),
            "allow_save": self.get_allow_publish_save(),
            "allow_email": self.get_allow_publish_email(),
            "custom_actions": custom_actions,
        }
        return config

    def ajax_render_reports(self, *args):
        """Renders all reports and returns the html

        This method also groups the reports by client
        """
        # update the request form with the parsed json data
        data = self.get_json()

        uids = data.get("items", [])
        template = data.get("template")
        paperformat = data.get("format", "A4")
        orientation = data.get("orientation", "portrait")
        # custom report options
        report_options = data.get("report_options", {})

        # generate the reports
        reports = self.generate_reports_for(uids,
                                            group_by=self.make_group_key,
                                            template=template,
                                            paperformat=paperformat,
                                            orientation=orientation,
                                            report_options=report_options)

        return "\n".join(map(lambda r: r.html, reports))

    @timeit()
    def ajax_save_reports(self):
        """Render all reports as PDFs and store them as AR Reports
        """
        # Data sent via async ajax call as JSON data from the frontend
        data = self.get_json()

        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # NOTE: It might also contain multiple reports!
        html = data.get("html")

        # get the triggered action (Save|Email)
        action = data.get("action", "save")

        # get the selected template
        template = data.get("template")

        # get the selected paperformat
        paperformat = data.get("format")

        # get the selected orientation
        orientation = data.get("orientation", "portrait")

        # get a timestamp
        timestamp = DateTime().ISO()

        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Print CSS: {}".format(css))

        # get the publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)

        # split the html per report
        # NOTE: each report is an instance of <bs4.Tag>
        html_reports = publisher.parse_reports(html)

        # extract the UIDs of each HTML report
        # NOTE: UIDs are injected in `.analysisrequest.reportview.render`
        report_uids = map(
            lambda report: report.get("uids", "").split(","), html_reports)

        # get the storage multi-adapter to save the generated PDFs
        storage = getMultiAdapter(
            (self.context, self.request), IPdfReportStorage)

        report_groups = []
        for html, uids in zip(html_reports, report_uids):
            # ensure we have valid UIDs here
            uids = filter(api.is_uid, uids)
            # convert the bs4.Tag back to pure HTML
            html = publisher.to_html(html)
            # wrap the report
            report = getMultiAdapter((html,
                                      map(self.to_model, uids),
                                      template,
                                      paperformat,
                                      orientation,
                                      None,
                                      publisher), interface=IReportWrapper)

            # BBB: inject contained UIDs into metadata
            metadata = report.get_metadata(
                contained_requests=uids, timestamp=timestamp)
            # store the report(s)
            objs = storage.store(report.pdf, html, uids, metadata=metadata)
            # append the generated reports to the list
            report_groups.append(objs)

        # NOTE: The reports might be stored in multiple places (clients),
        #       which makes it difficult to redirect to a single exit URL
        #       based on the action the users clicked (save/email)
        exit_urls = map(lambda reports: self.get_exit_url_for(
            reports, action=action), report_groups)

        if not exit_urls:
            return api.get_url(self.context)

        # Group the urls by path. This makes possible to at least return a
        # single url for multiple uids when the base path (e.g. client) is the
        # same. This is required for Single Reports, for which there are as many
        # report groups as samples, regardless of clients
        groups = OrderedDict()
        for url in exit_urls:
            base_path, uids = url.split("?uids=")
            path_uids = groups.get(base_path, "")
            groups[base_path] = ",".join(filter(None, [path_uids, uids]))
        return "?uids=".join(groups.items()[0])

    def get_exit_url_for(self, reports, action="save"):
        """Handle the response for the generated reports

        This method determines based on the generated reports where the browser
        should redirect the user and what status message to display.

        :param reports: List of report objects
        :returns: A single redirect URL
        """

        # view endpoint
        endpoint = action == "email" and "email" or "reports_listing"

        # get the report uids
        clients = []
        report_uids = []
        parent_titles = []

        for report in reports:
            parent = api.get_parent(report)
            if hasattr(parent, "getClient"):
                clients.append(parent.getClient())
            report_uids.append(api.get_uid(report))
            parent_titles.append(api.get_title(parent))

        # generate status message
        message = _("Generated reports for: {}".format(
            ", ".join(parent_titles)))
        self.add_status_message(message, level="info")

        # generate exit URL
        exit_url = self.context.absolute_url()
        if clients:
            exit_url = api.get_url(clients[0])

        exit_url = "{}/{}?uids={}".format(exit_url, endpoint,
                                          ",".join(report_uids))
        return exit_url

    def ajax_get_reports(self, *args):
        """Returns a list of JSON mmodels
        """
        uids = self.get_json().get("items") or args
        models = map(lambda uid: SuperModel(uid), uids)
        return map(lambda model: model.to_dict(), models)

    @timeit()
    def ajax_load_preview(self):
        """Recalculate the HTML of one rendered report after all the embedded
        JavaScripts modified the report on the client side.
        """
        # Data sent via async ajax call as JSON data from the frontend
        data = self.get_json()

        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!
        html = data.get("html")

        if self.get_developer_mode():
            return html

        # Metadata
        paperformat = data.get("format")
        orientation = data.get("orientation", "portrait")

        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Preview CSS: {}".format(css))

        # get an publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)

        # HTML image previews
        preview = u""

        # Generate PNG previews for the pages of each report
        for report_node in publisher.parse_reports(html):
            pages = publisher.write_png_pages(report_node)
            previews = map(lambda page: publisher.png_to_img(*page), pages)
            preview += "\n".join(previews)

        # Add the generated CSS to the preview, so that the container can grow
        # accordingly
        preview += "<style type='text/css'>{}</style>".format(css)
        return preview
