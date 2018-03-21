# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import inspect
from collections import Iterable, defaultdict
from operator import itemgetter

from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
from senaite.publisher import logger
from senaite.publisher.adapters import PublicationObject
from senaite.publisher.config import PAPERFORMATS
from senaite.publisher.decorators import returns_json
from senaite.publisher.interfaces import IPrintView
from weasyprint import HTML
from weasyprint.compat import base64_encode
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


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
        self.uids = self.request.get("items", "").split(",")
        self.reports = map(lambda uid: PublicationObject(uid), self.uids)
        return self.template()

    def render_report(self, obj):
        # TODO: template must be dynamic
        template = ViewPageTemplateFile("templates/reports/default.pt")

        portal = api.get_portal()
        setup = portal.bika_setup
        laboratory = setup.laboratory

        options = {
            "id": obj.getId(),
            "uid": obj.UID(),
            "portal": PublicationObject("0"),
            "setup": PublicationObject(api.get_uid(setup)),
            "laboratory": PublicationObject(api.get_uid(laboratory)),
        }

        return template(self, publication_object=obj, **options)

    def get_paperformats(self):
        """Returns a mapping of available paper formats
        """
        # Todo: Implement cascading lookup: client->registry->config
        return PAPERFORMATS

    def get_image_resource(self, name, prefix="bika.lims.images"):
        """Return the full image resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": self.context,
            "request": self.request,
            "domain": "bika",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    def group_items_by(self, key, items):
        """Group the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        results = defaultdict(list)
        for item in items:
            group_key = item[key]
            if callable(group_key):
                group_key = group_key()
            results[group_key].append(item)
        return results

    def sort_items_by(self, key, items, reverse=False):
        """Sort the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        if not callable(key):
            key = itemgetter(key)
        return sorted(items, key=key, reverse=reverse)


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

        wrapped = PublicationObject(uid)
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

    def ajax_load_preview(self):
        """Recalculate the HTML of one rendered report after all the embedded
        JavaScripts modified the report on the client side.
        """
        logger.info("ajax_load_preview")
        html = self.request.form.get("html").decode("utf8")
        whtml = HTML(string=u"{}".format(html),
                     base_url=api.get_portal().absolute_url())

        portal_url = api.get_portal().absolute_url()
        css_base_url = "{}/++resource++senaite.publisher.static/css".format(
            portal_url)
        print_css = "{}/print.css".format(css_base_url)
        report_css = "{}/report.css".format(css_base_url)

        document = whtml.render(enable_hinting=True,
                                stylesheets=[print_css, report_css])

        logger.info("Rendering {} Pages".format(len(document.pages)))
        images = []
        for page in document.pages:
            png_bytes, width, height = document.copy([page]).write_png()
            data_url = 'data:image/png;base64,' + (
                base64_encode(png_bytes).decode('ascii').replace('\n', ''))

            img = """<div class='report' style='width: {0}px; height: {1}px'>
                       <img src='{2}'/>
                     </div>""".format(width, height, data_url)
            images.append(img)

        return images
