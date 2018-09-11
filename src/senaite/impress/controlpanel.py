# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

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

    max_email_size = schema.Float(
        title=_(u"Maximum Email Size in MB"),
        description=_("Email sending will be disabled if the given limit is "
                      "exceeded"),
        default=10.0,
        min=0.0,
        required=True,
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
