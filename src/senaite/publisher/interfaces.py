# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

from zope.interface import Interface


class IPrintView(Interface):
    """Printing controller view
    """


class ITemplateOptionsProvider(Interface):
    """Provides a data dict which can be used for templates
    """


class IPublicationObject(Interface):
    """The content to be published
    """


class IPublisher(Interface):
    """HTML Publisher
    """
