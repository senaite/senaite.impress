# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import inspect
import json

from senaite.publisher import logger
from senaite.publisher.decorators import returns_json
from senaite.publisher.interfaces import IPublisher
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
        body = self.request.get("BODY", {})
        return json.loads(body)

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

    def ajax_templates(self):
        """Returns the available templates
        """
        return self.get_report_templates()

    def ajax_render_reports(self, *args):
        """Renders all reports and returns the html
        """
        # update the request form with the parsed json data
        body = self.get_json()
        self.request.form.update(body)
        return self.render_reports()

    def ajax_load_preview(self):
        """Recalculate the HTML of one rendered report after all the embedded
        JavaScripts modified the report on the client side.
        """
        # This is the html after it was rendered by the client browser and
        # eventually extended by JavaScript, e.g. Barcodes or Graphs added etc.
        # N.B. It might also contain multiple reports!
        html = self.request.form.get("html").decode("utf8")
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
