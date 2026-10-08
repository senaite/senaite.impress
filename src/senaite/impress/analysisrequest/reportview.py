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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from collections import Iterable
from collections import OrderedDict
from collections import Sequence
from itertools import chain
from operator import itemgetter
from string import Template

import DateTime
from bika.lims import POINTS_OF_CAPTURE
from bika.lims import api
from bika.lims.interfaces import IInternalUse
from bika.lims.utils import get_link
from bika.lims.utils.analysis import format_interim
from bika.lims.workflow import getTransitionDate
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFPlone.utils import safe_callable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as PT
from senaite.app.supermodel.interfaces import ISuperModel
from senaite.core.catalog.utils import sortable_sortkey_title
from senaite.impress import senaiteMessageFactory as _
from senaite.impress import logger
from senaite.impress.decorators import returns_super_model
from senaite.impress.reportview import ReportView as Base
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

SINGLE_TEMPLATE = Template("""<!-- Single Report -->
<div class="report" uids="${uids}" client_uid="${client_uid}">
  <script type="text/javascript">
    console.log("*** BEFORE TEMPLATE RENDER ***");
  </script>
  ${template}
</div>
""")

MULTI_TEMPLATE = Template("""<!-- Multi Report -->
<div class="report" uids="${uids}" client_uid="${client_uid}">
  <script type="text/javascript">
    console.log("*** BEFORE MULTI TEMPLATE RENDER ***");
  </script>
  ${template}
</div>
""")

# Registry fallbacks for report options that can be set per publication
REPORT_OPTION_DEFAULTS = {
    "sample_code": "barcode",
    "release_mode": "signatures",
    "accreditation_logo": "auto",
}

# Symbols used in the results table and explained in the legend
SYMBOL_ACCREDITED = u"★"
SYMBOL_ABOVE_RANGE = u"▲"
SYMBOL_BELOW_RANGE = u"▼"


def is_results_report(obj):
    """Checks if the given object is a stored PDF results report
    """
    return api.get_portal_type(obj) == "ResultsReport"


def format_address(address):
    """Returns the non-empty lines of an address record

    :param address: address record with the keys address, zip, city, country
    :returns: list of address lines
    """
    if not address:
        return []
    # AT address fields might return a list of records
    if isinstance(address, (list, tuple)):
        address = address[0]
    zip_city = u" ".join(filter(None, [
        address.get("zip"), address.get("city")]))
    lines = [address.get("address"), zip_city, address.get("country")]
    return filter(None, map(api.safe_unicode, lines))


def get_first_address(obj):
    """Returns the postal address of the object or its physical address
    """
    postal = format_address(obj.getPostalAddress())
    return postal or format_address(obj.getPhysicalAddress())


def css_string(value):
    """Returns the value as a quoted CSS string for the `content` property
    """
    value = api.safe_unicode(value or u"")
    value = value.replace(u"\\", u"\\\\").replace(u"\"", u"\\\"")
    return u"\"{}\"".format(value.replace(u"\n", u" "))


def get_capture_date(analysis):
    """Returns the result capture date of the analysis
    """
    return analysis.getResultCaptureDate()


def get_verifier_ids(analysis):
    """Returns the user IDs of the persons who verified the analysis
    """
    return filter(None, analysis.getVerificators() or [])


def is_same_day(date1, date2):
    """Checks if both DateTime objects fall on the same calendar day
    """
    return date1.Date() == date2.Date()


class ReportView(Base):
    """AR specific Report View
    """
    JS_TEMPLATE = PT("templates/js.pt")
    CSS_TEMPLATE = PT("templates/css.pt")
    CONTROLS_TEMPLATE = PT("templates/controls.pt")
    HEADER_TEMPLATE = PT("templates/header.pt")
    INFO_TEMPLATE = PT("templates/info.pt")
    ALERTS_TEMPLATE = PT("templates/alerts.pt")
    SUMMARY_TEMPLATE = PT("templates/summary.pt")
    RESULTS_TEMPLATE = PT("templates/results.pt")
    RESULTS_TRANSPOSED_TEMPLATE = PT("templates/results_transposed.pt")
    INTERPRETATIONS_TEMPLATE = PT("templates/interpretations.pt")
    REMARKS_TEMPLATE = PT("templates/remarks.pt")
    ATTACHMENTS_TEMPLATE = PT("templates/attachments.pt")
    SIGNATURE_TEMPLATE = PT("templates/signatures.pt")
    DISCREETER_TEMPLATE = PT("templates/discreeter.pt")
    FOOTER_TEMPLATE = PT("templates/footer.pt")

    def render_js(self, context, **kw):
        return self.JS_TEMPLATE(context, **kw)

    def render_css(self, context, **kw):
        return self.CSS_TEMPLATE(context, **kw)

    def render_controls(self, context, **kw):
        return self.CONTROLS_TEMPLATE(context, **kw)

    def render_header(self, context, **kw):
        return self.HEADER_TEMPLATE(context, **kw)

    def render_info(self, context, **kw):
        return self.INFO_TEMPLATE(context, **kw)

    def render_alerts(self, context, **kw):
        return self.ALERTS_TEMPLATE(context, **kw)

    def render_summary(self, context, **kw):
        return self.SUMMARY_TEMPLATE(context, **kw)

    def render_results(self, context, **kw):
        return self.RESULTS_TEMPLATE(context, **kw)

    def render_results_transposed(self, context, **kw):
        return self.RESULTS_TRANSPOSED_TEMPLATE(context, **kw)

    def render_interpretations(self, context, **kw):
        return self.INTERPRETATIONS_TEMPLATE(context, **kw)

    def render_remarks(self, context, **kw):
        return self.REMARKS_TEMPLATE(context, **kw)

    def render_attachments(self, context, **kw):
        return self.ATTACHMENTS_TEMPLATE(context, **kw)

    def render_signatures(self, context, **kw):
        return self.SIGNATURE_TEMPLATE(context, **kw)

    def render_discreeter(self, context, **kw):
        return self.DISCREETER_TEMPLATE(context, **kw)

    def render_footer(self, context, **kw):
        return self.FOOTER_TEMPLATE(context, **kw)

    @property
    def points_of_capture(self):
        items = POINTS_OF_CAPTURE.items()
        return OrderedDict(items)

    @property
    @returns_super_model
    def portal(self):
        return api.get_portal()

    @property
    def portal_url(self):
        return api.get_portal().absolute_url()

    @property
    @returns_super_model
    def setup(self):
        return self.portal.bika_setup

    @property
    @returns_super_model
    def laboratory(self):
        # Laboratory was migrated to Dexterity in senaite.core 2.7 and
        # now lives under `portal.setup` instead of `portal.bika_setup`.
        return api.get_senaite_setup().laboratory

    def get_accreditation_logo_url(self):
        """Returns the URL of the laboratory's accreditation body logo

        The laboratory was migrated to Dexterity in senaite.core 2.7, so the
        logo is a `NamedBlobImage` served through the standard `@@images`
        view instead of an Archetypes image with an `absolute_url`.

        :returns: the accreditation logo URL, or None if no logo is set
        """
        laboratory = api.get_senaite_setup().laboratory
        if not laboratory.getAccreditationBodyLogo():
            return None
        return "{}/@@images/accreditation_body_logo".format(
            api.get_url(laboratory))

    @property
    def current_user(self):
        user = api.get_current_user()
        # XXX: we're missing here LDAP properties!
        #      needs to be fixed in the API.
        properties = api.get_user_properties(user)
        properties.update({
            "userid": user.getId(),
            "username": user.getUserName(),
            "roles": user.getRoles(),
            "email": user.getProperty("email"),
            "fullname": user.getProperty("fullname"),
        })
        return properties

    @property
    def wf_tool(self):
        return api.get_tool("portal_workflow")

    @property
    def timestamp(self):
        return DateTime.DateTime()

    def to_localized_time(self, date, **kw):
        """Converts the given date to a localized time string
        """
        if date is None:
            return ""
        # default options
        options = {
            "long_format": True,
            "time_only": False,
            "context": api.get_portal(),
            "request": api.get_request(),
            "domain": "senaite.core",
        }
        options.update(kw)
        return ulocalized_time(date, **options)

    def get_resource_url(self, name, prefix=""):
        """Return the full resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)

    def get_footer_text(self, escape=True):
        """Returns the footer text from the setup
        """
        return api.get_registry_record("senaite.impress.footer")

    def get_analyses(self, model_or_collection):
        """Returns a flat list of all analyses for the given model or collection
        """
        collection = self.to_list(model_or_collection)
        analyses = chain(*map(lambda m: m.Analyses, collection))
        # Boil out analyses meant to be used for internal use only
        analyses = filter(lambda an: not IInternalUse.providedBy(an.instance),
                          analyses)
        return self.sort_items(analyses)

    def get_analyses_by(self, model_or_collection,
                        title=None, keyword=None, service_title=None,
                        poc=None, category=None,
                        hidden=False, retracted=False, rejected=False):
        """Returns a sorted list of Analyses for the given POC which are in the
        given Category
        """
        analyses = self.get_analyses(model_or_collection)
        if title is not None:
            analyses = filter(lambda an: an.Title() == title, analyses)
        if keyword is not None:
            analyses = filter(lambda an: an.getKeyword() == keyword, analyses)
        if service_title is not None:
            def get_service_title(analysis):
                service = analysis.getAnalysisService()
                return service.Title()
            analyses = filter(
                lambda an: get_service_title(an) == service_title, analyses)
        if poc is not None:
            analyses = filter(lambda an: an.PointOfCapture == poc, analyses)
        if category is not None:
            analyses = filter(lambda an: an.Category == category, analyses)
        if not hidden:
            analyses = filter(lambda an: not an.Hidden, analyses)
        if not retracted:
            def is_not_retracted(analysis):
                return analysis.review_state != "retracted"
            analyses = filter(is_not_retracted, analyses)
        if not rejected:
            def is_not_rejected(analysis):
                return analysis.review_state != "rejected"
            analyses = filter(is_not_rejected, analyses)
        return self.sort_items(analyses)

    def get_analyses_by_poc(self, model_or_collection):
        """Groups the given analyses by their point of capture
        """
        analyses = self.get_analyses(model_or_collection)
        groups = self.group_items_by("PointOfCapture", analyses)
        # Ensure always alphabetic sorting of PoC
        by_poc = OrderedDict()
        for key in sorted(groups):
            by_poc[key] = groups[key]
        return by_poc

    def get_analyses_by_category(self, model_or_collection):
        """Groups the Analyses by their Category
        """
        analyses = self.get_analyses(model_or_collection)
        return self.group_items_by("Category", analyses)

    def get_categories_by_poc(self, model_or_collection):
        """Groups the Categoris of the Analyses by their POC
        """
        categories_by_poc = dict()
        analyses_by_poc = self.get_analyses_by_poc(model_or_collection)
        for k, v in analyses_by_poc.items():
            categories_by_poc[k] = self.group_items_by("Category", v)
        return categories_by_poc

    def sort_items(self, items, reverse=False):
        """Default sort which mixes in the sort key
        """
        def sortable_title(obj):
            title = sortable_sortkey_title(obj)
            if safe_callable(title):
                title = title()
            return title

        def _cmp(obj1, obj2):
            st1 = sortable_title(obj1)
            st2 = sortable_title(obj2)
            return cmp(st1, st2)

        return sorted(items, cmp=_cmp, reverse=reverse)

    def group_items_by(self, key, items):
        """Group the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        results = OrderedDict()
        for item in items:
            group_key = item[key]
            if callable(group_key):
                group_key = group_key()
            if group_key not in results:
                results[group_key] = [item]
            else:
                results[group_key].append(item)
        return results

    def group_into_chunks(self, items, chunk_size=1):
        """Group items into chunks of the given size
        """
        if chunk_size > len(items):
            chunk_size = len(items)

        for i in range(0, len(items), chunk_size):
            yield items[i:i + chunk_size]

    def sort_items_by(self, key, items, reverse=False):
        """Sort the items (mappings with dict interface) by the given key
        """
        if not isinstance(items, Iterable):
            raise TypeError("Items must be iterable")
        if not callable(key):
            key = itemgetter(key)
        return sorted(items, key=key, reverse=reverse)

    def uniquify_items(self, items):
        """Uniquify the items with sort order
        """
        unique = []
        for item in items:
            if item in unique:
                continue
            unique.append(item)
        return unique

    def to_list(self, model_or_collection):
        if ISuperModel.providedBy(model_or_collection):
            return [model_or_collection]
        if isinstance(model_or_collection, Sequence):
            return model_or_collection
        raise TypeError("Need a model or collection")

    def hyphenize(self, string):
        """Replace minus (-) with the HTML entitiy &hyphen;

        This is needed for proper text wrapping on overflow
        """
        if not isinstance(string, basestring):
            return string
        return string.replace("-", "&hyphen;")

    def get_transition_date(self, obj, transition=None):
        """Returns the date of the given Transition
        """
        if self.is_model(obj):
            obj = obj.instance
        if transition is None:
            return None
        return getTransitionDate(obj, transition, return_as_datetime=True)

    def is_model(self, obj):
        """Check if the given object is a SuperModel
        """
        return ISuperModel.providedBy(obj)

    def get_result_variables(self, analysis, report_only=True):
        """Returns the result variables (aka interim fields) from the given
        analysis, with additional attributes formatted_result and
        formatted_unit. If report_only is True, only result variables that are
        flagged with attribute "report" are returned.

        :param analysis: Analysis' object/supermodel/brain or UID
        :param report_only: Only result variables flagged with 'report:True'
        :returns: List of result variable items
        """
        items = []
        obj = api.get_object(analysis)
        interim_fields = obj.getInterimFields() or []
        for interim_field in interim_fields:

            # skip interim not fields flagged with report
            if report_only and not interim_field.get("report", False):
                continue

            # apply formatting
            item = format_interim(interim_field)
            items.append(item)

        return items

    def is_true(self, val):
        """Returns whether val evaluates to True
        """
        if not val:
            return False
        val = str(val).strip().lower()
        return val in ["y", "yes", "1", "true", "on"]

    def get_attachment_link(self, attachment):
        """Returns a well-formed link for the attachment passed in
        """
        filename = attachment.getFilename()
        att_url = api.get_url(attachment)
        url = "{}/at_download/AttachmentFile".format(att_url)
        return get_link(url, filename, tabindex="-1")

    def format_condition(self, condition):
        """Returns a string representation of the analysis condition value
        """
        title = condition.get("title")
        value = condition.get("value", "")
        if not any([title, value]):
            return None

        texts = {True: _("Yes"), False: _("No")}
        condition_type = condition.get("type")
        if condition_type == "checkbox":
            value = texts.get(self.is_true(value))

        elif condition_type == "file":
            attachment = api.get_object_by_uid(value, None)
            if not attachment:
                return None
            value = self.get_attachment_link(attachment)

        return api.to_utf8(str(value))

    def get_analysis_conditions(self, analysis, report_only=True):
        """Returns the (pre)conditions from the given analysis, that have a
        valid value set, with the additional attribute 'formatted_value'. If
        'report_only' is True, only conditions that are flagged with attribute
        "report" are returned.

        :param analysis: Analysis' object/supermodel/brain or UID
        :param report_only: Only conditions flagged with 'report:True'
        :returns: List of anaysis conditions items
        """
        # analysis (pre)conditions
        items = []
        analysis = api.get_object(analysis)
        conditions = analysis.getConditions() or []
        for condition in conditions:

            # skip non-reportable conditions
            report = condition.get("report", False)
            if not self.is_true(report):
                continue

            # skip those without a valid format
            formatted = self.format_condition(condition)
            if not formatted:
                continue

            # apply formatting
            condition["formatted_value"] = formatted
            items.append(condition)

        return items

    def format_footnote(self, note, last=True):
        """Returns a condition or result variable as a single footnote text

        :param note: condition or interim mapping with title and value
        :param last: whether the note is the last one of the footnote
        :returns: text like `Title: Value Unit;`
        """
        value = u" ".join(filter(None, map(api.safe_unicode, [
            note.get("formatted_value"), note.get("formatted_unit")])))
        text = u"{}: {}".format(api.safe_unicode(note.get("title")), value)
        return text if last else u"{};".format(text)

    def get_report_option(self, options, name):
        """Returns the report option, falling back to the registry setting

        :param options: template options with the `report_options` mapping
        :param name: name of the report option and the registry record
        :returns: value of the option
        """
        report_options = options.get("report_options") or {}
        value = report_options.get(name)
        if value:
            return value
        default = REPORT_OPTION_DEFAULTS.get(name)
        record = "senaite.impress.{}".format(name)
        return api.get_registry_record(record, default=default) or default

    def get_choices(self, vocabulary_name):
        """Returns the terms of the named vocabulary as value/title dicts
        """
        factory = getUtility(IVocabularyFactory, vocabulary_name)
        vocabulary = factory(api.get_portal())
        return [{"value": term.value, "title": term.title}
                for term in vocabulary]

    def get_report_revision(self):
        """Returns the revision of the report for the primary sample

        The first publication is revision 1, every stored report of the
        primary sample increases the revision by one.
        """
        if not self.model:
            return 1
        revision = self.__dict__.get("_report_revision")
        if revision is None:
            objs = self.model.instance.objectValues()
            revision = len(filter(is_results_report, objs)) + 1
            self._report_revision = revision
        return revision

    def get_report_id(self):
        """Returns the identifier of the report, e.g. `W-0001-R1`
        """
        if not self.model:
            return u""
        return u"{}-R{}".format(
            self.model.getId(), self.get_report_revision())

    def get_client_address(self, model):
        """Returns the address lines of the client of the sample
        """
        client = model.instance.getClient()
        if not client:
            return []
        return get_first_address(client)

    def get_contact_fullname(self, model):
        """Returns the full name of the primary contact of the sample
        """
        contact = model.instance.getContact()
        return contact.getFullname() if contact else u""

    def get_laboratory_line(self):
        """Returns the laboratory name and address in a single line
        """
        laboratory = api.get_senaite_setup().laboratory
        name = laboratory.getName() or laboratory.Title()
        address = format_address(laboratory.getPhysicalAddress())
        return u" · ".join(map(api.safe_unicode, [name] + address))

    def get_css_string(self, value):
        """Returns the value as a quoted CSS string
        """
        return css_string(value)

    def get_reported_analyses(self, model_or_collection):
        """Returns the analyses that are visible in the report

        The analyses of a single sample are cached for the lifetime of the
        view, because several sections of the report need them.
        """
        if not ISuperModel.providedBy(model_or_collection):
            return self.get_analyses_by(model_or_collection)
        cache = self.__dict__.setdefault("_reported_analyses", {})
        uid = model_or_collection.UID()
        if uid not in cache:
            cache[uid] = self.get_analyses_by(model_or_collection)
        return cache[uid]

    def get_sampler_fullname(self, model):
        """Returns the full name of the sampler of the sample
        """
        sampler = model.instance.getSampler()
        if not sampler:
            return u""
        return api.get_user_fullname(sampler) or sampler

    def get_specification_title(self, model):
        """Returns the title of the specification used for the results
        """
        sample = model.instance
        spec = sample.getPublicationSpecification() or \
            sample.getSpecification()
        return api.get_title(spec) if spec else u""

    def format_date_range(self, start, end):
        """Returns a localized date or date range for the given dates
        """
        start_date = self.to_localized_time(start, long_format=0)
        if is_same_day(start, end):
            return start_date
        end_date = self.to_localized_time(end, long_format=0)
        return u"{} – {}".format(start_date, end_date)

    def get_test_period(self, model):
        """Returns the period in which the results were captured
        """
        analyses = self.get_reported_analyses(model)
        dates = filter(None, map(get_capture_date, analyses))
        if not dates:
            return u""
        return self.format_date_range(min(dates), max(dates))

    def get_sample_info(self, model):
        """Returns the label/value pairs shown below the sample header

        Only pairs with a value are returned.
        """
        sample = model.instance
        items = [
            (_("Date Sampled"),
             self.to_localized_time(sample.getDateSampled())),
            (_("Sampler"), self.get_sampler_fullname(model)),
            (_("Sampling Deviation"), sample.getSamplingDeviationTitle()),
            (_("Date Received"),
             self.to_localized_time(sample.getDateReceived())),
            (_("Condition on Receipt"), sample.getSampleConditionTitle()),
            (_("Environmental Conditions"),
             sample.getEnvironmentalConditions()),
            (_("Test Period"), self.get_test_period(model)),
            (_("Specification"), self.get_specification_title(model)),
        ]
        return [{"label": label, "value": value}
                for label, value in items if value]

    def has_uncertainties(self, model):
        """Checks if any reported analysis of the sample has an uncertainty
        """
        analyses = self.get_reported_analyses(model)
        return any(map(model.get_uncertainty, analyses))

    def has_specifications(self, model):
        """Checks if any reported analysis of the sample has a valid range
        """
        analyses = self.get_reported_analyses(model)
        return any(map(model.get_formatted_specs, analyses))

    def get_out_of_range_symbol(self, model, analysis):
        """Returns the symbol for a result above or below the valid range
        """
        if not model.is_out_of_range(analysis):
            return u""
        result = api.to_float(analysis.getResult(), None)
        if result is None:
            # e.g. a multi choice result, the direction is unknown
            return u""
        specs = analysis.getResultsRange()
        maximum = api.to_float(specs.get("max"), None)
        if maximum is not None and result > maximum:
            return SYMBOL_ABOVE_RANGE
        minimum = api.to_float(specs.get("min"), None)
        if minimum is not None and result < minimum:
            return SYMBOL_BELOW_RANGE
        return u""

    def get_range_comment(self, model, analysis):
        """Returns the comment of the specification for a result out of range

        The comment is set per analysis in the specification and is only
        reported when the result is out of the specified range.
        """
        if not model.is_out_of_range(analysis):
            return u""
        comment = analysis.getResultsRange().get("rangecomment")
        return api.safe_unicode(comment or u"").strip()

    def is_below_detection_limit(self, analysis):
        """Checks if the result is below the lower detection limit
        """
        return analysis.instance.isBelowLowerDetectionLimit()

    def is_above_detection_limit(self, analysis):
        """Checks if the result is above the upper detection limit
        """
        return analysis.instance.isAboveUpperDetectionLimit()

    def any_analysis(self, predicate):
        """Checks if the predicate is true for any reported analysis
        """
        return any(map(predicate, self.get_reported_analyses(
            self.collection)))

    def any_sample(self, predicate):
        """Checks if the predicate is true for any sample in the report
        """
        return any(map(predicate, self.collection))

    def get_legend(self):
        """Returns the symbols used in the report with their meaning
        """
        items = []
        if self.show_accreditation():
            items.append((SYMBOL_ACCREDITED, _("Accredited method")))
        if self.any_sample(self.has_out_of_range_results):
            items.append((u"{} {}".format(
                SYMBOL_ABOVE_RANGE, SYMBOL_BELOW_RANGE),
                _("Result above or below the specified range")))
        if self.any_analysis(self.is_below_detection_limit):
            items.append((u"<", _(
                "Result below the lower detection limit; the limit is given")))
        if self.any_analysis(self.is_above_detection_limit):
            items.append((u">", _(
                "Result above the upper detection limit; the limit is given")))
        if self.any_analysis(lambda an: an.isRetest()):
            items.append((u"RT", _("Result of a retest")))
        if self.any_sample(self.has_uncertainties):
            items.append((u"U", _("Expanded measurement uncertainty")))
        return [{"symbol": symbol, "text": text} for symbol, text in items]

    def has_out_of_range_results(self, model):
        """Checks if any reported result of the sample is out of range
        """
        analyses = self.get_reported_analyses(model)
        return any(map(model.is_out_of_range, analyses))

    def show_accreditation(self):
        """Checks if the accreditation statement is shown

        Only valid reports of an accredited laboratory with at least one
        accredited analysis carry the accreditation statement.
        """
        laboratory = api.get_senaite_setup().laboratory
        if not laboratory.getLaboratoryAccredited():
            return False
        if self.any_sample(lambda model: model.is_provisional()):
            return False
        return self.any_analysis(lambda an: an.getAccredited())

    def get_accreditation_body(self):
        """Returns the accreditation body with the accreditation reference

        :returns: text like `ANAB (L-2291)`
        """
        laboratory = api.get_senaite_setup().laboratory
        body = api.safe_unicode(laboratory.getAccreditationBody() or u"")
        reference = api.safe_unicode(
            laboratory.getAccreditationReference() or u"")
        if not reference:
            return body
        return u"{} ({})".format(body, reference)

    def show_accreditation_logo(self, options):
        """Checks if the accreditation logo and statement are shown

        The report option `accreditation_logo` shows them always or never.
        Automatic applies the rules of `show_accreditation`. In any case
        the laboratory must be accredited.

        :param options: template options with the `report_options` mapping
        """
        laboratory = api.get_senaite_setup().laboratory
        if not laboratory.getLaboratoryAccredited():
            return False
        mode = self.get_report_option(options, "accreditation_logo")
        if mode == "hide":
            return False
        if mode == "show":
            return True
        return self.show_accreditation()

    def get_person_info(self, user):
        """Returns name, job title and signature URL for the given user
        """
        contact = api.get_user_contact(user, contact_types=["LabContact"])
        if not contact:
            return {
                "fullname": api.get_user_fullname(user),
                "jobtitle": u"",
                "signature_url": None,
            }
        signature = contact.getSignature()
        return {
            "fullname": contact.getFullname(),
            "jobtitle": contact.getJobTitle(),
            "signature_url": "{}/Signature".format(
                api.get_url(contact)) if signature else None,
        }

    def get_manager_info(self, manager):
        """Returns name, job title and signature URL for a lab manager
        """
        return {
            "fullname": manager.getFullname(),
            "jobtitle": manager.getJobTitle(),
            "signature_url": "{}/Signature".format(
                manager.absolute_url()) if manager.getSignature() else None,
        }

    def get_responsibles(self):
        """Returns the persons that verified the results of the report

        Falls back to the department managers when no verifier is known,
        e.g. for samples that were verified automatically.
        """
        analyses = self.get_reported_analyses(self.collection)
        userids = chain(*map(get_verifier_ids, analyses))
        users = filter(None, map(api.get_user, self.uniquify_items(userids)))
        if users:
            return map(self.get_person_info, users)
        managers = chain(*map(lambda model: model.managers, self.collection))
        return map(self.get_manager_info, self.uniquify_items(managers))

    def is_provisional_report(self):
        """Checks if the report contains results that are not verified yet

        Invalidated samples were verified, they are flagged by the alerts.
        """
        return self.any_sample(
            lambda model: model.is_provisional() and not model.is_invalid())

    def get_publisher_fullname(self):
        """Returns the full name of the user publishing the report
        """
        user = api.get_current_user()
        return api.get_user_fullname(user) or user.getId()


class SingleReportView(ReportView):
    """View for Single Reports
    """

    def __init__(self, model, request):
        logger.info("SingleReportView::__init__:model={}"
                    .format(model))
        super(SingleReportView, self).__init__(model, request)
        # always provide a collection for simplicity
        self.collection = [model]
        self.model = model
        self.request = request

    def render(self, template, **kw):
        context = self.get_template_context(self.model, **kw)
        template = Template(template).safe_substitute(context)
        return SINGLE_TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, model, **kw):
        context = {
            "uids": model.UID(),
            "client_uid": model.getClientUID(),
        }
        context.update(kw)
        return context


class MultiReportView(ReportView):
    """View for Multi Reports
    """

    def __init__(self, collection, request):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        super(MultiReportView, self).__init__(collection, request)
        self.collection = collection
        # consider the first sample of the collection as the primary model
        self.model = collection[0] if len(collection) > 0 else None
        self.request = request

    def render(self, template, **kw):
        """Wrap the template and render
        """
        context = self.get_template_context(self.collection, **kw)
        template = Template(template).safe_substitute(context)
        return MULTI_TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, collection, **kw):
        if not collection:
            return {}
        uids = map(lambda m: m.uid, collection)
        client_uid = collection[0].getClientUID()
        context = {
            "uids": ",".join(uids),
            "client_uid": client_uid,
        }
        context.update(kw)
        return context
