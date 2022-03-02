# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS.
#
# SENAITE.IMPRESS is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2022 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.interfaces import IBikaLIMS
from zope.interface import Attribute
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class ILayer(IBikaLIMS):
    """Layer Interface
    """


class ISenaiteImpressLayer(ILayer):
    """Senaite Impress Browser Layer Interface
    """


class ISenaiteImpressHtmlHead(IViewletManager):
    """A viewlet manager that sits in the <head> of the rendered page
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


class IPublisher(Interface):
    """HTML -> PDF Publishing Engine
    """


class ITemplateFinder(Interface):
    """Utility to find template resources
    """


class IPdfReportStorage(Interface):
    """Storage adapter for report PDFs
    """

    def store(pdf, html, uids, metadata):
        """Stores the generated PDF for the given UIDs in a location and
        returns a list of generated report objects.
        """


class IReportWrapper(Interface):
    """Wrapper class for reports
    """
    pdf = Attribute("Generate PDF data")

    def get_metadata(**kw):
        """Generate metadata for the report
        """
