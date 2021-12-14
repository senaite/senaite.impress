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
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import itertools

from bika.lims.utils import format_supsub
from bika.lims.utils import formatDecimalMark
from bika.lims.utils import to_utf8
from bika.lims.utils.analysis import format_uncertainty
from bika.lims import api
from senaite.app.supermodel import SuperModel as BaseModel
from senaite.impress import logger
from senaite.impress.decorators import returns_super_model
from math import floor
from math import log10


class SuperModel(BaseModel):
    """Analysis Request SuperModel
    """

#Start Custom Methods
    def get_nitrogen_conversion_effeciency(self):
        total_n = 0
        no3 = 0
        nh4 = 0
        ncr = ''

        found = False
        for i in range(20, 0, -1):
            if found==False:
                version = 'sap_total_nitrogen-'+str(i)
                if hasattr(self,version):
                    found = True
                    total_n = float(self[version].Result)
        if found == False and hasattr(self,'sap_total_nitrogen'):
            if self.sap_total_nitrogen.Result == '':
                total_n = 'NT'
            else:
                total_n = float(self.sap_total_nitrogen.Result)

        found = False
        for i in range(20, 0, -1):
            if found==False:
                version = 'sap_nitrogen_as_nitrate-'+str(i)
                if hasattr(self,version):
                    found = True
                    no3 = float(self[version].Result)
        if found == False and hasattr(self,'sap_nitrogen_as_nitrate'):
            if self.sap_nitrogen_as_nitrate.Result == '':
                no3 = 'NT'
            else:
                no3 = float(self.sap_nitrogen_as_nitrate.Result)

        found = False
        for i in range(20, 0, -1):
            if found==False:
                version = 'sap_nitrogen_as_ammonium-'+str(i)
                if hasattr(self,version):
                    found = True
                    nh4 = float(self[version].Result)
        if found == False and hasattr(self,'sap_nitrogen_as_ammonium'):
            if self.sap_nitrogen_as_ammonium.Result == '':
                nh4 = 'NT'
            else:
                nh4 = float(self.sap_nitrogen_as_ammonium.Result)

        if total_n == 'NT' or no3 == 'NT' or nh4 == 'NT':
            ncr = 'NT'
        elif total_n < 0.01:
            ncr = '-'
        else:
            if total_n == '':
                total_n = 0
            if nh4 == '' or nh4 < 0:
                nh4 = 0
            if no3 == '' or no3 < 0:
                no3 = 0
            print("total nitrogen is: " + str(total_n))
            print("nitrogen as nitrate is: " + str(no3))
            print("nitrogen as ammonium is: " + str(nh4))
            ncr = float(1 - ((nh4 + no3)/total_n))*100

            ncr = round(ncr, 3-int(floor(log10(abs(ncr))))-1)

        return ncr

    def get_project_contact(self):
        batch = api.get_object(self.getBatch())
        project_contact = batch.getReferences(relationship="SDGProjectContact")[0]
        project_contact_name = project_contact.Firstname + " " + project_contact.Surname
        return project_contact_name

    def get_grower_contact(self):
        batch = api.get_object(self.getBatch())
        project_contact = batch.getReferences(relationship="SDGGrowerContact")[0]
        project_contact_name = ''
        if project_contact:
            project_contact_name = project_contact.Firstname + " " + project_contact.Surname
        return project_contact_name

    def get_attachment_file(self):
        attachment = self.Attachment[0]
        return attachment

    def get_attachment_files(self):
        attachments = []
        for i in self.Attachment:
            attachments.append(i)
        return attachments

    def get_analyst_initials(self, analysis):
        return analysis.getAnalystInitials()

    def get_optimal_high_level(self, keyword):
        max = ''
        for i in self.getResultsRange():
            if i['keyword'] ==  keyword:
                max = i.get('max', '')
        return max

    def get_optimal_low_level(self, keyword):
        min = ''
        for i in self.getResultsRange():
            if i['keyword'] ==  keyword:
                min = i.get('min', '')
        return min

    def get_result_bar_percentage(self, keyword):

        specs = ''
        for i in self.getResultsRange():
            if i['keyword'] ==  keyword:
                specs = i

        perc = 0
        if specs:
            found = False
            for i in range(10, 0, -1):
                if found==False:
                    version = keyword+'-'+str(i)
                    if hasattr(self,version):
                        found = True
                        result_str = str(self[version].Result).strip()
                        ldl = 0.01
            if found == False and hasattr(self,keyword):
                result_str = str(self[keyword].Result).strip()
                ldl = 0.01

            min_str = str(specs.get('min', 0)).strip()
            max_str = str(specs.get('max', 99999)).strip()
            min = -1
            max = -1
            result = -1

            try:
                min = float(min_str)
            except ValueError:
                pass
            try:
                max = float(max_str)
            except ValueError:
                pass
            try:
                result = float(result_str)
            except ValueError:
                pass

            if result < ldl:
                result = 0
            if min != -1 and max != -1 and result != -1 and max != 0:
                if result <= min:
                    perc = (result/min)*(100/3)
                elif result >= max:
                    perc = (200/3) + ((100/3)-(100/3)/(result/max))
                else:
                    perc = (100/3) + (((result-min)/(max-min))*(100/3))
        return perc

    def get_effeciency_percentage(self, analysis):

        found = False
        analyte = None
        for j in range(20, 0, -1):
            if found==False:
                sap_version = analysis+str(j)
                if hasattr(self,sap_version):
                    found = True
                    analyte = self[sap_version]
        if found == False and hasattr(self,analysis):
            analyte = self[analysis]

        found = False
        total_n = None
        for j in range(20, 0, -1):
            if found==False:
                sap_version = 'sap_total_nitrogen'+str(j)
                if hasattr(self,sap_version):
                    found = True
                    total_n = self[sap_version]
        if found == False and hasattr(self,'sap_total_nitrogen'):
            total_n = self.sap_total_nitrogen

        result = None
        tn = None
        perc = None

        if analyte is None:
            result = 0
        else:
            result = analyte.getResult()

        if total_n is None:
            tn = 0
        else:
            tn = total_n.getResult()

        if tn is None or tn == 0 or not tn.replace('.', '', 1).isdigit():
            perc = 0
        elif (result is None or result == 0 or not result.replace('.', '', 1).isdigit()):
            perc = 0
        else:
            perc = (float(result)/float(tn))*100

        return perc

    def get_conversion_effeciency_percentage(self):

        found = False
        n_as_ammonium = None
        for j in range(20, 0, -1):
            if found==False:
                sap_version = 'sap_nitrogen_as_ammonium'+str(j)
                if hasattr(self,sap_version):
                    found = True
                    n_as_ammonium = self[sap_version]
        if found == False and hasattr(self,'sap_nitrogen_as_ammonium'):
            n_as_ammonium = self.sap_nitrogen_as_ammonium

        found = False
        n_as_nitrate = None
        for j in range(20, 0, -1):
            if found==False:
                sap_version = 'sap_nitrogen_as_nitrate'+str(j)
                if hasattr(self,sap_version):
                    found = True
                    n_as_nitrate = self[sap_version]
        if found == False and hasattr(self,'sap_nitrogen_as_nitrate'):
            n_as_nitrate = self.sap_nitrogen_as_nitrate

        found = False
        total_n = None
        for j in range(20, 0, -1):
            if found==False:
                sap_version = 'sap_total_nitrogen'+str(j)
                if hasattr(self,sap_version):
                    found = True
                    total_n = self[sap_version]
        if found == False and hasattr(self,'sap_total_nitrogen'):
            total_n = self.sap_total_nitrogen

        no3 = None
        nh4 = None
        tn = None
        perc = None

        if n_as_ammonium is None:
            nh4 = 0
        else:
            nh4 = n_as_ammonium.getResult()
            # nh4_str = str(nh4).strip()

        if n_as_nitrate is None:
            no3 = 0
        else:
            no3 = n_as_nitrate.getResult()
            # no3_str = str(no3).strip()

        if total_n is None:
            tn = 0
        else:
            tn = total_n.getResult()
            # tn_str = str(tn).strip()

        if tn is None or tn == 0 or not tn.replace('.', '', 1).isdigit():
            perc = 0
        elif (no3 is None or no3 == 0 or not no3.replace('.', '', 1).isdigit()) and (nh4 is None or nh4 == 0 or not nh4.replace('.', '', 1).isdigit()):
            perc = 0
        else:
            perc = (1 - ((float(no3)+float(nh4))/float(tn)))*100

        print('no3 is: {0} and isdigit is {1}'.format(no3,no3.replace('.', '', 1).isdigit()))
        print('nh4 is: {0} and isdigit is {1}'.format(nh4,nh4.replace('.', '', 1).isdigit()))
        print('tn is: {0} and isdigit is {1}'.format(tn,tn.replace('.', '', 1).isdigit()))
        print('perc is: {0}'.format(perc))
        return perc

    def get_formatted_result_or_NT(self, analysis, digits):
        """Return formatted result or NT
        """
        result = analysis.getResult()
        if analysis is None or result == "":
            return "NT" #Only if Analysis Service is listed, but not filled out
        elif float(result) < 0.01:
            return "< " + "0.01"
        else:
            result = float(result)
            result = round(result, digits-int(floor(log10(abs(result))))-1)
            if result >= 10:
                result = int(result)
            return result

    def get_liqfert_sf(self, analysis, digits):
        """Return formatted result or NT
        """
        result = analysis.getResult()
        choices = analysis.getResultOptions()
        if choices:
            # Create a dict for easy mapping of result options
            values_texts = dict(map(
                lambda c: (str(c["ResultValue"]), c["ResultText"]), choices
            ))

            # Result might contain a single result option
            match = values_texts.get(str(result))
            if match:
                return match

        if analysis is None or result == "":
            return "NT" #Only if Analysis Service is listed, but not filled out
        #Common Citizen Hack
        elif self.getClient().ClientID == "NAL20-004" and analysis.Keyword in ('liqfert_nickel','liqfert_copper'):
            if float(result) < 0.02:
                return "< 0.02"
            else:
                result = float(result)
                result = round(result, digits-int(floor(log10(abs(result))))-1)
                if result >= 100:
                    result = int(result)
                return result
        elif self.getClient().ClientID == "NAL20-004" and analysis.Keyword == 'liqfert_molybdenum':
            if float(result) < 0.01:
                return "< 0.01"
            else:
                result = float(result)
                result = round(result, digits-int(floor(log10(abs(result))))-1)
                if result >= 100:
                    result = int(result)
                return result
        #End Common Citizen Hack
        elif float(result) < float(analysis.getLowerDetectionLimit()):
            return "< " + str(analysis.getLowerDetectionLimit())
        elif float(result) > float(analysis.getUpperDetectionLimit()):
            if analysis.getUpperDetectionLimit() >= 10000:
                return "> " + str(int(analysis.getUpperDetectionLimit()))
            else:
                return "> " + str(analysis.getUpperDetectionLimit())
        elif analysis.Keyword in ('surface_ecoli_mpn_10x','surface_coliform_mpn_10x','surface_ecoli_mpn_100x','surface_coliform_mpn_100x','surface_coliform_mpn','surface_ecoli_mpn'):
            result = float(result)
            if result < 100:
                result = round(result, digits-int(floor(log10(abs(result))))-1)
            if result >= 100 and result < 1000:
                result = round(result, 4-int(floor(log10(abs(result))))-1)
                intresult = int(result)
                if intresult == result: result = intresult
            if result >= 1000 and result < 10000:
                result = round(result, 5-int(floor(log10(abs(result))))-1)
            if result >= 10000:
                result = round(result, 5-int(floor(log10(abs(result))))-1)
                result = int(result)
            return result
        else:
            result = float(result)
            result = round(result, digits-int(floor(log10(abs(result))))-1)
            if result >= 100:
                result = int(result)
            return result

    def get_received_date(self):
        """Returns the batch date formatted as [Month Day, Year]
        """
        batch = api.get_object(self.getBatch())
        try:
            received_date = batch.SDGDate.strftime("%b %d, %Y")
            return received_date or ""
        except TypeError:
            raise TypeError("No SDG Recieved Date")
#End Custom Methods

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
