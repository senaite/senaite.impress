# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

from zope.interface import Interface


class IReportModel(Interface):
    """A Report Model wrapper
    """


class IReportModelCollection(Interface):
    """A collection of Report Models
    """


class IReportView(Interface):
    """Single Report View
    """


class IMultiReportView(Interface):
    """Multi Report View
    """


class IPrintView(Interface):
    """Print View
    """


class IPublisher(Interface):
    """HTML -> PDF Publishing Engine
    """


class ITemplateFinder(Interface):
    """Utility to find template resources
    """
