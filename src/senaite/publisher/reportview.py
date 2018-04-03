# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import json
import os
from collections import Iterable
from collections import OrderedDict
from collections import defaultdict
from operator import itemgetter
from string import Template

from bika.lims import POINTS_OF_CAPTURE
from bika.lims.utils import format_supsub
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import to_utf8
from bika.lims.utils.analysis import format_uncertainty
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite import api
from senaite.publisher import logger
from senaite.publisher.decorators import returns_report_model
from senaite.publisher.interfaces import IReportView
from zope.interface import implements

TEMPLATE = Template("""<!-- Report Template ${id} -->
<div class="report" id="${id}" uid="${uid}">
  <script type="text/javascript">
    console.log("*** BEFORE TEMPLATE RENDER ${id} ***");
  </script>
  ${template}
</div>
""")


class ReportView(object):
    """View for a single Report
    """
    implements(IReportView)

    def __init__(self, context, request):
        logger.info("ReportView::__init__:context={}".format(context.id))
        self.context = context
        self.request = request
        self.template = self.default_template

    def render(self, **kw):
        if self.is_page_template():
            template = ViewPageTemplateFile(self.template)(self, **kw)
        else:
            with open(self.template, "r") as template:
                template = template.read()

        context = self.template_context
        template = Template(template).safe_substitute(context)
        return TEMPLATE.safe_substitute(context, template=template)

    @property
    def template_context(self):
        return {
            "id": self.context.getId(),
            "uid": self.context.UID(),
            "user": json.dumps(self.current_user),
            "api": {
                "report": self.get_api_url(self.context),
                "setup": self.get_api_url(self.setup),
                "laboratory": self.get_api_url(self.laboratory),
            }
        }

    def get_api_url(self, reportmodel):
        """Returns the API URL for the passed in object
        """
        info = {
            "uid": reportmodel.UID(),
            "endpoint": "ajax_printview",
            "action": "get",
            "base_url": self.portal.absolute_url(),
        }
        return "{base_url}/{endpoint}/{action}/{uid}".format(**info)

    def is_page_template(self):
        _, ext = os.path.splitext(self.template)
        if ext in [".pt", ".zpt"]:
            return True
        return False

    def set_template(self, template):
        self.template = template

    @property
    def default_template(self):
        return "templates/reports/default.pt"

    @property
    @returns_report_model
    def portal(self):
        return api.get_portal()

    @property
    @returns_report_model
    def setup(self):
        return self.portal.bika_setup

    @property
    @returns_report_model
    def laboratory(self):
        return self.setup.laboratory

    @property
    def current_user(self):
        user = api.get_current_user()
        return api.get_user_properties(user)

    @property
    def scientific_notation(self):
        return int(self.setup.getScientificNotationReport())

    @property
    def decimal_mark(self):
        return self.context.aq_parent.getDecimalMark()

    @property
    @returns_report_model
    def departments(self):
        return self.context.getDepartments()

    @property
    def managers(self):
        out = []
        for dept in self.departments:
            manager = dept.Manager
            if not manager:
                continue
            if manager in out:
                continue
            out.append(manager)
        return out

    @property
    def resultsinterpretation(self):
        ri_by_depts = self.context.ResultsInterpretationDepts

        out = []
        for ri in ri_by_depts:
            dept = ri.get("uid", "")
            title = getattr(dept, "title", "")
            richtext = ri.get("richtext", "")
            out.append({"title": title, "richtext": richtext})

        return out

    def is_invalid(self):
        return self.context.isInvalid()

    def is_provisional(self):
        if self.is_invalid():
            return True
        valid_states = ['verified', 'published']
        states = self.context.getObjectWorkflowStates().values()
        if not any(map(lambda s: s in valid_states, states)):
            return True
        return False

    def is_out_of_range(self, analysis):
        """Check if the analysis is out of range
        """
        from bika.lims.api.analysis import is_out_of_range
        return is_out_of_range(analysis.instance)[0]

    def is_retested(self, analysis):
        """Check if the analysis is retested
        """
        return analysis.getRetested()

    @property
    def points_of_capture(self):
        items = POINTS_OF_CAPTURE.items()
        return OrderedDict(items)

    def get_analyses_by_poc(self):
        """Returns a dictionary of POC -> Analyses
        """
        return self.group_items_by("getPointOfCapture", self.context.Analyses)

    def get_categories_in_poc(self, poc):
        """Returns a list of sorted Categories in the given POC
        """
        an_in_poc = self.get_analyses_by_poc().get(poc)
        categories = set(map(lambda an: an.Category, an_in_poc))
        return self.sort_items(categories)

    def get_analyses(self, poc=None, cat=None, include_hidden=False):
        """Returns a sorted list of Analyses for the given POC which are in the
        given Category
        """
        analyses = self.context.Analyses
        if poc is not None:
            analyses = filter(lambda an: an.PointOfCapture == poc, analyses)
        if cat is not None:
            analyses = filter(lambda an: an.Category == cat, analyses)
        if not include_hidden:
            analyses = filter(lambda an: not an.Hidden, analyses)
        return self.sort_items(analyses)

    def group_items_by(self, key, items):
        """Group the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        results = defaultdict(list)
        for item in items:
            group_key = item[key]
            if callable(group_key):
                group_key = group_key()
            results[group_key].append(item)
        return results

    def sort_items_by(self, key, items, reverse=False):
        """Sort the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        if not callable(key):
            key = itemgetter(key)
        return sorted(items, key=key, reverse=reverse)

    def sort_items(self, items, reverse=False):
        """Default sort which mixes in the sort key
        """
        def sortable_title(obj):
            sort_key = obj.get("SortKey") or 0.0
            title = obj.title.lower()
            return u"{:010.3f}{}".format(sort_key, title)

        def _cmp(obj1, obj2):
            st1 = sortable_title(obj1)
            st2 = sortable_title(obj2)
            return cmp(st1, st2)

        return sorted(items, cmp=_cmp, reverse=reverse)

    def get_formatted_unit(self, analysis):
        """Return formatted Unit
        """
        return format_supsub(to_utf8(analysis.Unit))

    def get_formatted_result(self, analysis):
        """Return formatted result
        """
        return analysis.getFormattedResult(
            specs=analysis.getResultsRange(),
            sciformat=self.scientific_notation,
            decimalmark=self.decimal_mark)

    def get_formatted_uncertainty(self, analysis):
        uncertainty = format_uncertainty(
            analysis.instance,
            analysis.getResult(),
            decimalmark=self.decimal_mark,
            sciformat=self.scientific_notation)
        return "[&plusmn; {}]".format(uncertainty)

    def get_formatted_specs(self, analysis):
        specs = analysis.getResultsRange()
        specs["min"] = 1
        specs["max"] = 10
        fs = ''
        if specs.get('min', None) and specs.get('max', None):
            fs = '%s - %s' % (specs['min'], specs['max'])
        elif specs.get('min', None):
            fs = '> %s' % specs['min']
        elif specs.get('max', None):
            fs = '< %s' % specs['max']
        return formatDecimalMark(fs, self.decimal_mark)

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": self.context,
            "request": self.request,
            "domain": "bika",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    def get_image_resource(self, name, prefix="bika.lims.images"):
        """Return the full image resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)

    def sort_attachments(self, attachments=[]):
        """Attachment sorter
        """
        inf = float("inf")
        view = self.context.restrictedTraverse("attachments_view")
        order = view.get_attachments_order()

        def att_cmp(att1, att2):
            _n1 = att1.get('uid')
            _n2 = att2.get('uid')
            _i1 = _n1 in order and order.index(_n1) + 1 or inf
            _i2 = _n2 in order and order.index(_n2) + 1 or inf
            return cmp(_i1, _i2)

        return sorted(attachments, cmp=att_cmp)
