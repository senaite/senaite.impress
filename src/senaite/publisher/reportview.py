# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.


from collections import Iterable
from collections import defaultdict
from operator import itemgetter

from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
from senaite.publisher import logger
from senaite.publisher.interfaces import IReportView
from senaite.publisher.decorators import returns_publication_object
from zope.interface import implements


class ReportView(object):
    """View for a single Report
    """
    implements(IReportView)

    def __init__(self, context, request):
        logger.info("ReportView::__init__:context={}".format(context.id))
        self.context = context
        self.request = request

    def render(self, **kw):
        return self.template(self, **kw)

    @property
    def template(self):
        return ViewPageTemplateFile("templates/reports/default.pt")

    @property
    @returns_publication_object
    def portal(self):
        return api.get_portal()

    @property
    @returns_publication_object
    def setup(self):
        return self.portal.bika_setup

    @property
    @returns_publication_object
    def laboratory(self):
        return self.setup.laboratory

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

    def get_image_resource(self, name, prefix="bika.lims.images"):
        """Return the full image resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)
