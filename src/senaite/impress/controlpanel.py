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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from senaite.impress import senaiteMessageFactory as _
from senaite.impress.interfaces import ITemplateFinder
from plone.supermodel import model
from zope import schema
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def default_templates(context):
    finder = getUtility(ITemplateFinder)
    templates = finder.get_templates()
    return [t[0] for t in templates]


class IImpressControlPanel(Interface):
    """Controlpanel Settings
    """

    templates = schema.List(
        title=_(u"Available Templates"),
        description=_("Please choose the templates that can be selected"),
        required=True,
        defaultFactory=default_templates,
        value_type=schema.Choice(
            title=_(u"Active templates"),
            source="senaite.impress.vocabularies.Templates",
        )
    )

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

    footer = schema.Text(
        title=_(u"Footer Text"),
        description=_("The footer text will be rendered on every PDF page "
                      "and may contain arbitrary HTML"),
        default=u"",
        required=False,
    )

    store_multireports_individually = schema.Bool(
        title=_(u"Store Multi-Report PDFs Individually"),
        description=_("Store generated multi-report PDFs individually. "
                      "Turn off to store the multi-report PDF only for the "
                      "primary item of the report"),
        default=True,
        required=False,
    )

    developer_mode = schema.Bool(
        title=_(u"Developer Mode"),
        description=_("Returns the raw HTML in the report preview."),
        default=False,
        required=False,
    )

    allow_pdf_download = schema.Bool(
        title=_(u"Allow PDF download"),
        description=_(u"Allow direct download of the generated report"),
        default=False,
        required=False,
    )

    allow_pdf_email_share = schema.Bool(
        title=_(u"Allow PDF email share"),
        description=_(u"Allow to share the generated PDF directly via email"),
        default=False,
        required=False,
    )

    reload_after_reorder = schema.Bool(
        title=_(u"Reload after reorder"),
        description=_(u"Reload report automatically when items order changed"),
        default=False,
        required=False,
    )

    ###
    # Fieldsets
    ###
    model.fieldset(
        "report_settings",
        label=_(u"Report Settings"),
        # description=_(""),
        fields=[
            "footer",
        ],
    )

    model.fieldset(
        "advanced",
        label=_(u"Advanced"),
        # description=_(""),
        fields=[
            "reload_after_reorder",
            "allow_pdf_download",
            "allow_pdf_email_share",
            "store_multireports_individually",
            "developer_mode",
        ],
    )


class ImpressControlPanelForm(RegistryEditForm):
    schema = IImpressControlPanel
    schema_prefix = "senaite.impress"
    label = _("SENAITE IMPRESS Settings")


ImpressControlPanelView = layout.wrap_form(
    ImpressControlPanelForm, ControlPanelFormWrapper)
