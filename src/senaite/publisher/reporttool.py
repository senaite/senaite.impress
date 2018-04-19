# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

from collections import Iterable
from collections import defaultdict
from itertools import chain
from operator import itemgetter

from senaite.publisher.interfaces import IReportModel
from senaite.publisher.interfaces import IReportTool
from zope.interface import implements


class ReportTool(object):
    """Tool to handle report models and collections
    """
    implements(IReportTool)

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
        if isinstance(model_or_collection, list):
            return model_or_collection
        raise TypeError("Need a model or collection")


class ARReportTool(ReportTool):
    """AR specific report tool to handle AR based models/collections
    """

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
