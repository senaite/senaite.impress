# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

from zope.interface import Interface


class IPublicationObject(Interface):
    """Model: Wraps a content to be published
    """


class IReportView(Interface):
    """View: Renders a Publication Object
    """


class IPrintView(Interface):
    """Controller: Publishes Reports
    """


class IPublisher(Interface):
    """HTML -> PDF Publishing Engine
    """
