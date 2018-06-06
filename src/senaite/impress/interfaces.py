# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from zope.interface import Interface
from bika.lims.interfaces import IBikaLIMS


class ILayer(IBikaLIMS):
    """Layer Interface
    """


class IPublishView(Interface):
    """Publish View
    """


class IReportView(Interface):
    """Single Report View
    """


class IMultiReportView(Interface):
    """Multi Report View
    """


class IReportModel(Interface):
    """A Report Model wrapper
    """


class IPublisher(Interface):
    """HTML -> PDF Publishing Engine
    """


class ITemplateFinder(Interface):
    """Utility to find template resources
    """
