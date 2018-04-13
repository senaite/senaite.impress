# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

import inspect
import json

from senaite.publisher import logger
from senaite.publisher.decorators import returns_json
from senaite.publisher.publishview import PublishView
from senaite.publisher.reportmodel import ReportModel
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class AjaxPublishView(PublishView):
    """Print View with Ajax exposed methods
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
        """Return the JSONified

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

    def ajax_default_template(self):
        """Returns the default template
        """
        return self.get_default_template()

    def ajax_render_reports(self, *args):
        """Renders all reports and returns the html
        """
        # update the request form with the parsed json data
        data = self.get_json()
        items = data.pop("items", [])
        return self.render_reports(uids=items, **data)

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
        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!
        data = self.get_json()
        html = data.pop("html", None)

        publisher = self.get_publisher(html, **data)
        merge = data.get("merge", False)
        images = publisher.write_png(merge=merge)

        css = self.get_print_css(**data)
        logger.info(u"Preview CSS: {}".format(css))

        preview = u""
        for image in images:
            preview += publisher.png_to_img(*image)
        preview += u"<style type='text/css'>{}</style>".format(css)
        return preview
