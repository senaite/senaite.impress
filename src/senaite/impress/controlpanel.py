# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS.
#
# SENAITE.IMPRESS is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA.
#
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.formwidget.namedfile.widget import NamedFileFieldWidget
from plone.supermodel import model
from plone.z3cform import layout
from senaite.core.schema.registry import DataGridRow
from senaite.core.z3cform.widgets.datagrid import DataGridWidgetFactory
from senaite.impress import senaiteMessageFactory as _
from senaite.impress.interfaces import ITemplateFinder
from zope import schema
from zope.component import getUtility
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import Interface


@provider(IContextAwareDefaultFactory)
def default_templates(context):
    finder = getUtility(ITemplateFinder)
    templates = finder.get_templates()
    return [t[0] for t in templates]


class IPaperFormat(Interface):
    """Row schema for custom paper formats
    """

    key = schema.TextLine(
        title=_(u"Key"),
        description=_(u"Unique format identifier"),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Display name"),
        required=True,
    )

    page_width = schema.Float(
        title=_(u"Width (mm)"),
        required=True,
    )

    page_height = schema.Float(
        title=_(u"Height (mm)"),
        required=True,
    )

    margin_top = schema.Float(
        title=_(u"Top (mm)"),
        required=True,
    )

    margin_right = schema.Float(
        title=_(u"Right (mm)"),
        required=True,
    )

    margin_bottom = schema.Float(
        title=_(u"Bottom (mm)"),
        required=True,
    )

    margin_left = schema.Float(
        title=_(u"Left (mm)"),
        required=True,
    )


class ITemplateFormatMapping(Interface):
    """Row schema for template-to-format mappings
    """

    template = schema.Choice(
        title=_(u"Template"),
        vocabulary="senaite.impress.vocabularies.Templates",
        required=True,
    )

    format = schema.Choice(
        title=_(u"Paper Format"),
        vocabulary="senaite.impress.vocabularies.Paperformats",
        required=True,
    )


class IImpressControlPanel(model.Schema):
    """Controlpanel Settings
    """

    templates = schema.List(
        title=_(u"Available Templates"),
        description=_(
            "Please choose the templates that can be selected"),
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
        description=_(
            "The footer text will be rendered on every PDF page "
            "and may contain arbitrary HTML"),
        default=u"",
        required=False,
    )

    store_multireports_individually = schema.Bool(
        title=_(u"Store Multi-Report PDFs Individually"),
        description=_(
            "Store generated multi-report PDFs individually. "
            "Turn off to store the multi-report PDF only for "
            "the primary item of the report"),
        default=True,
        required=False,
    )

    developer_mode = schema.Bool(
        title=_(u"Developer Mode"),
        description=_(
            "Returns the raw HTML in the report preview."),
        default=False,
        required=False,
    )

    allow_pdf_download = schema.Bool(
        title=_(u"Allow PDF download"),
        description=_(
            u"Allow direct download of the generated report"),
        default=False,
        required=False,
    )

    allow_pdf_email_share = schema.Bool(
        title=_(u"Allow PDF email share"),
        description=_(
            u"Allow to share the generated PDF directly "
            u"via email"),
        default=False,
        required=False,
    )

    reload_after_reorder = schema.Bool(
        title=_(u"Reload after reorder"),
        description=_(
            u"Reload report automatically when items "
            u"order changed"),
        default=False,
        required=False,
    )

    # Use NamedFileFieldWidget to avoid PIL errors
    # (same pattern as site_logo in senaite.core)
    directives.widget("report_logo", NamedFileFieldWidget)
    report_logo = schema.Bytes(
        title=_(u"Report Logo"),
        description=_(
            u"Custom logo to display in report headers. "
            u"If not set, the default SENAITE logo is used."),
        required=False,
    )

    directives.widget(
        "paperformats",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    paperformats = schema.List(
        title=_(u"Custom Paper Formats"),
        description=_(
            u"Define custom paper formats with specific "
            u"dimensions and margins. Use the key to reference "
            u"the format in template mappings. If a key matches "
            u"a built-in format (e.g. A4), it overrides it."),
        value_type=DataGridRow(
            title=u"Paper Format",
            schema=IPaperFormat),
        required=False,
        default=[],
    )

    directives.widget(
        "template_format_mapping",
        DataGridWidgetFactory,
        allow_insert=True,
        allow_delete=True,
        allow_reorder=True,
        auto_append=True)
    template_format_mapping = schema.List(
        title=_(u"Template Format Mapping"),
        description=_(
            u"Map report templates to default paper formats. "
            u"When a template is selected, the mapped format "
            u"is automatically applied."),
        value_type=DataGridRow(
            title=u"Mapping",
            schema=ITemplateFormatMapping),
        required=False,
        default=[],
    )

    ###
    # Fieldsets
    ###
    model.fieldset(
        "report_settings",
        label=_(u"Report Settings"),
        fields=[
            "report_logo",
            "paperformats",
            "template_format_mapping",
            "footer",
        ],
    )

    model.fieldset(
        "advanced",
        label=_(u"Advanced"),
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
