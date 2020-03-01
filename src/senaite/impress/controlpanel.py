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
# Copyright 2018-2020 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from senaite.impress import senaiteMessageFactory as _
from zope import schema
from zope.interface import Interface


class IImpressControlPanel(Interface):
    """Controlpanel Settings
    """

    default_template = schema.Choice(
        title=_(u"Default Template"),
        description=_("Initially loaded report template"),
        vocabulary="senaite.impress.vocabularies.Templates",
        default="senaite.impress:MultiDefault.pt",
        required=True,
    )

    default_paperformat = schema.Choice(
        title=_(u"Default Paper Format"),
        description=_("Initially loaded paper format"),
        vocabulary="senaite.impress.vocabularies.Paperformats",
        default="A4",
        required=True,
    )

    default_orientation = schema.Choice(
        title=_(u"Default Orientation"),
        description=_("Initially loaded orientation"),
        vocabulary="senaite.impress.vocabularies.Orientations",
        default="portrait",
        required=True,
    )

    store_multireports_individually = schema.Bool(
        title=_(u"Store Multi-Report PDFs Individually"),
        description=_("Store generated multi-report PDFs individually. "
                      "Turn off to store the multi-report PDF only for the "
                      "primary item of the report"),
        default=True,
        required=False,
    )

    footer = schema.Text(
        title=_(u"Footer Text"),
        description=_("The footer text will be rendered on every PDF page "
                      "and may contain arbitrary HTML"),
        default=u"",
        required=False,
    )

    developer_mode = schema.Bool(
        title=_(u"Developer Mode"),
        description=_("Returns the raw HTML in the report preview."),
        default=False,
        required=False,
    )


class ImpressControlPanelForm(RegistryEditForm):
    schema = IImpressControlPanel
    schema_prefix = "senaite.impress"
    label = _("SENAITE IMPRESS Settings")


ImpressControlPanelView = layout.wrap_form(
    ImpressControlPanelForm, ControlPanelFormWrapper)
