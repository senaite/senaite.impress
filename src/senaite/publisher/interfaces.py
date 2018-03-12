# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

from zope.interface import Interface


class IPrintView(Interface):
    """Publisher Print View
    """


class IPublicationObject(Interface):
    """An object to be published
    """
