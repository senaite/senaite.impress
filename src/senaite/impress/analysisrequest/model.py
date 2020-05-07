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

import itertools

from bika.lims.utils import format_supsub
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import to_utf8
from bika.lims.utils.analysis import format_uncertainty
from bika.lims import api
from senaite.core.supermodel import SuperModel as BaseModel
from senaite.impress import logger
from senaite.impress.decorators import returns_super_model


class SuperModel(BaseModel):
    """Analysis Request SuperModel
    """

    def is_invalid(self):
        return self.isInvalid()

    def is_provisional(self):
        if self.is_invalid():
            return True
        valid_states = ['verified', 'published']
        return api.get_review_status(self.instance) not in valid_states

    def is_out_of_range(self, analysis):
        """Check if the analysis is out of range
        """
        from bika.lims.api.analysis import is_out_of_range
        return is_out_of_range(analysis.instance)[0]

    def is_retest(self, analysis):
        """Check if the analysis is a retest
        """
        return analysis.isRetest()

    def get_workflow_by_id(self, wfid):
        """Returns a workflow by ID

        :returns: DCWorkflowDefinition instance
        """
        wf_tool = api.get_tool("portal_workflow")
        return wf_tool.getWorkflowById(wfid)

    def get_transitions(self):
        """Return possible transitions
        """
        wf_tool = api.get_tool("portal_workflow")
        return wf_tool.getTransitionsFor(self.instance)

    def get_workflow_history(self, wfid, reverse=True):
        """Return the (reversed) review history
        """
        wf_tool = api.get_tool("portal_workflow")
        history = wf_tool.getHistoryOf(wfid, self.instance)
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

    @property
    def scientific_notation(self):
        setup = api.get_setup()
        return int(setup.getScientificNotationReport())

    @property
    def decimal_mark(self):
        return self.aq_parent.getDecimalMark()

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

    def get_resultsinterpretation(self):
        ri_by_depts = self.ResultsInterpretationDepts

        out = []
        for ri in ri_by_depts:
            dept = ri.get("uid", "")
            title = getattr(dept, "title", "")
            richtext = ri.get("richtext", "")
            out.append({"title": title, "richtext": richtext})

        return out

    def get_sorted_attachments(self, option="r"):
        """Return the sorted AR/AN Attachments with the given Report Option set
        """
        ar_attachments = self.Attachment
        an_attachments = [a for a in itertools.chain(*map(
            lambda an: an.Attachment, self.Analyses))]
        attachments = filter(lambda a: a.getReportOption() == option,
                             ar_attachments + an_attachments)
        return self.sort_attachments(attachments)

    def get_sorted_ar_attachments(self, option="r"):
        """Return the sorted AR Attchments with the given Report Option set
        """
        # AR attachments in the correct order
        attachments = self.sort_attachments(self.Attachment)
        # Return filtered list by report option
        return filter(lambda a: a.getReportOption() == option, attachments)

    def get_sorted_an_attachments(self, option="r"):
        """Return the sorted AN Attchments with the given Report Option set
        """
        attachments = []
        for analysis in self.Analyses:
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
        view = self.restrictedTraverse("attachments_view")
        order = view.get_attachments_order()

        def att_cmp(att1, att2):
            _n1 = att1.UID()
            _n2 = att2.UID()
            _i1 = _n1 in order and order.index(_n1) + 1 or inf
            _i2 = _n2 in order and order.index(_n2) + 1 or inf
            return cmp(_i1, _i2)

        return sorted(attachments, cmp=att_cmp)

    @property
    @returns_super_model
    def departments(self):
        return self.getDepartments()

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
    def verifiers(self):
        """Returns a list of user objects
        """
        out = []
        userids = reduce(lambda v1, v2: v1+v2,
                         map(lambda v: v.Verificators.split(","),
                             self.Analyses))
        for userid in set(userids):
            user = api.get_user(userid)
            if user is None:
                logger.warn("Could not find user '{}'".format(userid))
                continue
            out.append(user)
        return out
