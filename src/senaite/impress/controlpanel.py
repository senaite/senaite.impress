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

    default_template = schema.Choice(
        title=_(u"Default Template"),
        vocabulary="senaite.impress.vocabularies.Templates",
        default="senaite.impress:MultiDefault.pt",
        required=True,
    )

    default_paperformat = schema.Choice(
        title=_(u"Default Paper Format"),
        vocabulary="senaite.impress.vocabularies.Paperformats",
        default="A4",
        required=True,
    )

    default_orientation = schema.Choice(
        title=_(u"Default Orientation"),
        vocabulary="senaite.impress.vocabularies.Orientations",
        default="portrait",
        required=True,
    )

    max_email_size = schema.Float(
        title=_(u"Maximum Email Size in MB"),
        default=10.0,
        min=0.0,
        required=True,
    )


class ImpressControlPanelForm(RegistryEditForm):
    schema = IImpressControlPanel
    schema_prefix = "senaite.impress"
    label = _("SENAITE IMPRESS Settings")


ImpressControlPanelView = layout.wrap_form(
    ImpressControlPanelForm, ControlPanelFormWrapper)
