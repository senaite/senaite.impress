# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from senaite.publisher import senaiteMessageFactory as _
from zope import schema
from zope.interface import Interface


class IPublisherControlPanel(Interface):

    default_template = schema.Choice(
        title=_(u"Default Template"),
        vocabulary="senaite.publisher.vocabularies.Templates",
        default="senaite.publisher:MultiDefault.pt",
        required=True,
    )

    default_paperformat = schema.Choice(
        title=_(u"Default Paper Format"),
        vocabulary="senaite.publisher.vocabularies.Paperformats",
        default="A4",
        required=True,
    )

    default_orientation = schema.Choice(
        title=_(u"Default Orientation"),
        vocabulary="senaite.publisher.vocabularies.Orientations",
        default="portrait",
        required=True,
    )


class PublisherControlPanelForm(RegistryEditForm):
    schema = IPublisherControlPanel
    schema_prefix = "senaite.publisher"
    label = _("SENAITE Publisher Settings")


PublisherControlPanelView = layout.wrap_form(
    PublisherControlPanelForm, ControlPanelFormWrapper)
