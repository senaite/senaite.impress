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

from collections import Iterable
from collections import OrderedDict
from collections import Sequence
from itertools import chain
from operator import itemgetter
from string import Template

import DateTime
from bika.lims import POINTS_OF_CAPTURE
from bika.lims.interfaces import IInternalUse
from bika.lims.workflow import getTransitionDate
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.CMFPlone.utils import safe_unicode
from bika.lims import api
from senaite.core.supermodel.interfaces import ISuperModel
from senaite.impress import logger
from senaite.impress.decorators import returns_super_model
from senaite.impress.reportview import ReportView as Base


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


class ReportView(Base):
    """AR specific Report View
    """

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
        return self.setup.laboratory

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
                        title=None, service_title=None,
                        poc=None, category=None,
                        hidden=False, retracted=False, rejected=False):
        """Returns a sorted list of Analyses for the given POC which are in the
        given Category
        """
        analyses = self.get_analyses(model_or_collection)
        if title is not None:
            analyses = filter(lambda an: an.Title() == title, analyses)
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
        return self.group_items_by("PointOfCapture", analyses)

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
            sort_key = obj.get("SortKey") or 0.0
            title = obj.title.lower()
            return u"{:010.3f}{}".format(sort_key, safe_unicode(title))

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


class SingleReportView(ReportView):
    """View for Single Reports
    """

    def __init__(self, model, request):
        logger.info("SingleReportView::__init__:model={}"
                    .format(model))
        super(SingleReportView, self).__init__(model, request)
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
