# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from senaite.impress.interfaces import IReportView
from zope.interface import implements


class ReportView(object):
    """Generic Report View

    Note: This is also the base class for the Multi Report View
    """
    implements(IReportView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self, template):
        raise NotImplemented("Must be implemented by subclass")
