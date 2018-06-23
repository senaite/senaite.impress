# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import json
from collections import Iterable
from collections import OrderedDict
from collections import Sequence
from collections import defaultdict
from itertools import chain
from operator import itemgetter
from string import Template

import DateTime
from bika.lims import POINTS_OF_CAPTURE
from Products.CMFPlone.i18nl10n import ulocalized_time
from senaite import api
from senaite.impress import logger
from senaite.impress.decorators import returns_report_model
from senaite.impress.interfaces import IReportModel
from senaite.impress.reportview import ReportView as Base


SINGLE_TEMPLATE = Template("""<!-- Single Report -->
<div class="report" id="${id}" uid="${uid}">
  <script type="text/javascript">
    console.log("*** BEFORE TEMPLATE RENDER ${id} ***");
  </script>
  ${template}
</div>
""")

MULTI_TEMPLATE = Template("""<!-- Multi Report -->
<div class="report">
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
            "domain": "bika",
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
        setup = self.setup
        footer = setup.getResultFooter().decode("utf-8")
        if escape:
            return footer.replace("\r\n", "\A")
        return footer

    def get_analyses(self, model_or_collection):
        """Returns a flat list of all analyses for the given model or collection
        """
        collection = self.to_list(model_or_collection)
        analyses = chain(*map(lambda m: m.Analyses, collection))
        return self.sort_items(analyses)

    def get_analyses_by(self, model_or_collection,
                        title=None, poc=None, category=None,
                        hidden=False, retracted=False):
        """Returns a sorted list of Analyses for the given POC which are in the
        given Category
        """
        analyses = self.get_analyses(model_or_collection)
        if title is not None:
            analyses = filter(lambda an: an.Title() == title, analyses)
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
            return u"{:010.3f}{}".format(sort_key, title)

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

    def to_list(self, model_or_collection):
        if IReportModel.providedBy(model_or_collection):
            return [model_or_collection]
        if isinstance(model_or_collection, Sequence):
            return model_or_collection
        raise TypeError("Need a model or collection")


class SingleReportView(ReportView):
    """View for Single Reports
    """

    def __init__(self, model):
        logger.info("SingleReportView::__init__:model={}"
                    .format(model))
        super(SingleReportView, self).__init__(model=model)
        self.model = model
        self.context = model.instance
        self.request = api.get_request()

    def render(self, template):
        context = self.get_template_context(self.model)
        template = Template(template).safe_substitute(context)
        return SINGLE_TEMPLATE.safe_substitute(context, template=template)

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


class MultiReportView(ReportView):
    """View for Multi Reports
    """

    def __init__(self, collection):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        super(MultiReportView, self).__init__(collection=collection)
        self.collection = collection
        self.request = api.get_request()

        # needed for template rendering
        self.context = api.get_portal()

    def render(self, template):
        """Wrap the template and render
        """
        context = {}  # additional context before rendering
        template = Template(template).safe_substitute(context)
        return MULTI_TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, collection):
        return {}
