# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

import json
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
from senaite import api
from senaite.publisher import logger
from senaite.publisher.decorators import returns_report_model
from senaite.publisher.interfaces import IReportView
from zope.globalrequest import getRequest
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

    def __init__(self, model):
        logger.info("ReportView::__init__:model={}"
                    .format(model))
        self.model = model
        self.context = model
        self.request = getRequest()

    def render(self, template):
        context = self.get_template_context(self.model)
        template = Template(template).safe_substitute(context)
        return TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, model):
        return {
            "id": model.getId(),
            "uid": model.UID(),
            # XXX temporary piggypack solution to handle DateTime objects right
            "user": json.dumps(model.stringify(self.current_user)),
            "api": {
                "report": self.get_api_url(model),
                "setup": self.get_api_url(self.setup),
                "laboratory": self.get_api_url(self.laboratory),
            }
        }

    def get_api_url(self, model):
        """Returns the API URL for the passed in object
        """
        info = {
            "uid": model.UID(),
            "endpoint": "ajax_printview",
            "action": "get",
            "base_url": self.portal.absolute_url(),
        }
        return "{base_url}/{endpoint}/{action}/{uid}".format(**info)

    def get_resource_url(self, name, prefix=""):
        """Return the full resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)

    @property
    @returns_report_model
    def portal(self):
        return api.get_portal()

    @property
    def portal_url(self):
        return api.get_portal().absolute_url()

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
        properties = {
            "username": user.getId()
        }

        import pdb; pdb.set_trace()
        properties.update(api.get_user_properties(user))
        return properties

    @property
    def wf_tool(self):
        return api.get_tool("portal_workflow")


class ARReportView(ReportView):
    """AR specific Report View
    """

    @property
    def scientific_notation(self):
        return int(self.setup.getScientificNotationReport())

    @property
    def decimal_mark(self):
        return self.model.aq_parent.getDecimalMark()

    @property
    @returns_report_model
    def departments(self):
        return self.model.getDepartments()

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
        ri_by_depts = self.model.ResultsInterpretationDepts

        out = []
        for ri in ri_by_depts:
            dept = ri.get("uid", "")
            title = getattr(dept, "title", "")
            richtext = ri.get("richtext", "")
            out.append({"title": title, "richtext": richtext})

        return out

    def is_invalid(self):
        return self.model.isInvalid()

    def is_provisional(self):
        if self.is_invalid():
            return True
        valid_states = ['verified', 'published']
        states = self.model.getObjectWorkflowStates().values()
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
        return self.group_items_by("getPointOfCapture", self.model.Analyses)

    def get_categories_in_poc(self, poc):
        """Returns a list of sorted Categories in the given POC
        """
        an_in_poc = self.get_analyses_by_poc().get(poc)
        categories = set(map(lambda an: an.Category, an_in_poc))
        return self.sort_items(categories)

    def get_analyses(self, poc=None, cat=None, hidden=False, retracted=False):
        """Returns a sorted list of Analyses for the given POC which are in the
        given Category
        """
        analyses = self.model.Analyses
        if poc is not None:
            analyses = filter(lambda an: an.PointOfCapture == poc, analyses)
        if cat is not None:
            analyses = filter(lambda an: an.Category == cat, analyses)
        if not hidden:
            analyses = filter(lambda an: not an.Hidden, analyses)
        if not retracted:
            def is_not_retracted(analysis):
                return analysis.review_state != "retracted"
            analyses = filter(is_not_retracted, analyses)
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

    def group_into_chunks(self, items, chunk_size=1):
        """Group items into chunks of the given sizesize
        """
        if chunk_size > len(items):
            chunk_size = len(items)
        return zip(*[iter(items)] * chunk_size)

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
            "context": self.model.instance,
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

    def get_sorted_ar_attachments(self, option="r"):
        """Return the sorted AR Attchments with the given Report Option set
        """
        # AR attachments in the correct order
        attachments = self.sort_attachments(self.model.Attachment)
        # Return filtered list by report option
        return filter(lambda a: a.getReportOption() == option, attachments)

    def get_sorted_an_attachments(self, option="r"):
        """Return the sorted AN Attchments with the given Report Option set
        """
        attachments = []
        for analysis in self.model.Analyses:
            for attachment in self.sort_attachments(analysis.Attachment):
                if attachment.getReportOption() != option:
                    continue
                # Append a tuples of analysis, attachment
                attachments.append((analysis, attachment))
        return attachments

    def sort_attachments(self, attachments=[]):
        """Attachment sorter
        """
        inf = float("inf")
        view = self.model.restrictedTraverse("attachments_view")
        order = view.get_attachments_order()

        def att_cmp(att1, att2):
            _n1 = att1.UID()
            _n2 = att2.UID()
            _i1 = _n1 in order and order.index(_n1) + 1 or inf
            _i2 = _n2 in order and order.index(_n2) + 1 or inf
            return cmp(_i1, _i2)

        return sorted(attachments, cmp=att_cmp)

    def get_workflow_by_id(self, wfid):
        """Returns a workflow by ID

        :returns: DCWorkflowDefinition instance
        """
        return self.wf_tool.getWorkflowById(wfid)

    def get_workflows(self):
        """Return a list of assigned workflows
        """
        workflows = self.wf_tool.getChainFor(self.model.instance)
        return map(self.get_workflow_by_id, workflows)

    def get_transitions(self):
        """Return possible transitions
        """
        return self.wf_tool.getTransitionsFor(self.model.instance)

    def get_workflow_history(self, wfid, reverse=True):
        """Return the (reversed) review history
        """
        wf_tool = api.get_tool("portal_workflow")
        history = wf_tool.getHistoryOf(wfid, self.model.instance)
        if reverse:
            return history[::-1]
        return history

    def get_workflow_info_for(self, wfid):
        """Return a workflow info object
        """
        workflow = self.get_workflow_by_id(wfid)
        # the state variable, e.g. review_state
        state_var = workflow.state_var
        # tuple of possible transitions
        transitions = self.get_transitions()
        # review history tuple, e.g. ({'action': 'publish', ...}, )
        history = self.get_workflow_history(wfid)
        # the most current history info
        current_state = history[0]
        # extracted status id
        status = current_state[state_var]
        # `StateDefinition` instance
        state_definition = workflow.states[status]
        # status title, e.g. "Published"
        status_title = state_definition.title
        # return selected workflow information for the wrapped instance
        return {
            "id": wfid,
            "status": status,
            "status_title": status_title,
            "state_var": state_var,
            "transitions": transitions,
            "review_history": history,
        }

    def get_transition_date(self, wfid, state):
        """Return the date when the transition was made
        """
        wf = self.get_workflow_info_for(wfid)

        for rh in wf.get("review_history"):
            if rh.get("review_state") == state:
                return rh.get("time")
        return None

    def get_footer_text(self, escape=True):
        """Returns the footer text from the setup
        """
        setup = self.setup
        footer = setup.getResultFooter().decode("utf-8")
        if escape:
            return footer.replace("\r\n", "\A")
        return footer
