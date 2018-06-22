# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import inspect
import json

from DateTime import DateTime
from senaite import api
from senaite.impress import logger
from senaite.impress.decorators import returns_json
from senaite.impress.publishview import PublishView
from senaite.impress.reportmodel import ReportModel
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
        return func(*args)

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

        model = ReportModel(uid)
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
        config = {
            "format": self.get_default_paperformat(),
            "orientation": self.get_default_orientation(),
            "template": self.get_default_template(),
            "merge": False,
        }
        return config

    def ajax_render_reports(self, *args):
        """Renders all reports and returns the html
        """
        # update the request form with the parsed json data
        data = self.get_json()
        items = data.pop("items", [])
        return self.render_reports(uids=items, **data)

    def ajax_save_reports(self):
        """Render all reports as PDFs and store them as AR Reports
        """
        # Data sent via async ajax call as JSON data from the frontend
        data = self.get_json()

        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!
        html = data.get("html")

        # This is the clicked button name from the ReactJS component
        action = data.get("action", "save")

        # Metadata
        paperformat = data.get("format")
        template = data.get("template")
        orientation = data.get("orientation", "portrait")
        merge = data.get("merge", False)
        timestamp = DateTime().ISO8601()
        multi = self.is_multi_template(template)

        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Print CSS: {}".format(css))

        # get an publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)

        # generate the PDFs
        pdfs = publisher.write_pdf(html, merge=merge)
        exit_url = self.context.absolute_url()

        # We want to save the PDFs per AR as ARReport contents
        items = filter(None, data.get("items", []))
        ars = map(api.get_object_by_uid, items)

        # return if no ARs were found
        if not ars:
            logger.error("ajax_save_reports: No ARs found!")
            return exit_url

        # The primary AR
        primary_ar = ars[0]
        primary_client_url = primary_ar.getClient().absolute_url()

        # The new created ARReports
        reports = []

        # Generate the AR Reports
        for num, ar in enumerate(ars):
            pdf = pdfs[0]
            # there should be one PDF per AR in this case
            if not multi:
                pdf = pdfs[num]
            uid = api.get_uid(ar)
            title = "Report-{}".format(ar.getId())
            report = api.create(ar, "ARReport", title=title)
            _html = html
            if not merge:
                _html = publisher.get_reports(html, attrs={"uid": uid})
            report.edit(
                AnalysisRequest=uid,
                Pdf=pdf,
                Html=_html,
                # extended fields
                ContainedAnalysisRequests=ars if multi else ar,
                Metadata={
                    "template": template,
                    "paperformat": paperformat,
                    "orientation": orientation,
                    "timestamp": timestamp,
                    "multi": multi,
                },
            )
            reports.append(report)

        endpoint = "reports_listing"
        if action == "email":
            report_uids = map(api.get_uid, reports)
            if multi:
                report_uids = report_uids[:1]
            endpoint = "email?uids={}".format(",".join(report_uids))
        exit_url = "{}/{}".format(primary_client_url, endpoint)
        return exit_url

    def ajax_get_reports(self, *args):
        """Returns a list of JSON mmodels
        """
        uids = self.get_json().get("items") or args
        models = map(lambda uid: ReportModel(uid), uids)
        return map(lambda model: model.to_dict(), models)

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

        # Metadata
        paperformat = data.get("format")
        orientation = data.get("orientation", "portrait")
        merge = data.get("merge", False)

        # Generate the print CSS with the set format/orientation
        css = self.get_print_css(
            paperformat=paperformat, orientation=orientation)
        logger.info(u"Preview CSS: {}".format(css))

        # get an publisher instance
        publisher = self.publisher
        # add the generated CSS to the publisher
        publisher.add_inline_css(css)

        # generate the PNGs
        images = publisher.write_png(html, merge=merge)

        preview = u""
        for image in images:
            preview += publisher.png_to_img(*image)
        # Add the generated CSS to the preview, so that the container can grow
        # accordingly
        preview += "<style type='text/css'>{}</style>".format(css)
        return preview
