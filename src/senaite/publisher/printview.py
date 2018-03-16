# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.


import inspect
import json
from collections import Iterable, defaultdict
from operator import itemgetter

from DateTime import DateTime
from Products.CMFPlone.i18nl10n import ulocalized_time
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ZCatalog.Lazy import LazyMap
from senaite import api
from senaite.publisher import logger
from senaite.publisher.config import PAPERFORMATS
from senaite.publisher.decorators import returns_json
from senaite.publisher.interfaces import IPrintView, IPublicationObject
from zope.component import queryAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class PublicationObject(object):
    """Publication Content Wrapper

    This wrapper exposes the schema fields of the wrapped content object as
    attributes. The schema field values are looked up by their accessors.

    If the primary catalog of the wrapped object contains a metadata column
    with the same name as the accessor, the metadata colum value is used
    instead.
    """
    implements(IPublicationObject)

    def __init__(self, uid):
        logger.debug("PublicationObject({})".format(uid))

        self._uid = uid
        self._brain = None
        self._catalog = None
        self._instance = None

        self.__empty_marker = object
        self.data = dict()

    def __repr__(self):
        return "<{}:UID({})>".format(
            self.__class__.__name__, self.uid)

    def __str__(self):
        return self.uid

    def __hash__(self):
        return hash(self.uid)

    def __getitem__(self, key):
        value = self.get(key, self.__empty_marker)
        if value is not self.__empty_marker:
            return value
        raise KeyError(key)

    def __getattr__(self, name):
        value = self.get(name, self.__empty_marker)
        if value is not self.__empty_marker:
            return value
        # tab completion in pdbpp
        if name == "__members__":
            return self.keys()
        raise AttributeError(name)

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        return self.instance.Schema().keys()

    def iteritems(self):
        for k in self:
            yield (k, self[k])

    def iterkeys(self):
        return self.__iter__()

    def values(self):
        return [v for _, v in self.iteritems()]

    def items(self):
        return list(self.iteritems())

    def get_field(self, name, default=None):
        accessor = getattr(self.instance, "getField", None)
        if accessor is None:
            return default
        return accessor(name)

    def get(self, name, default=None):
        # Internal lookup in the data dict
        value = self.data.get(name, self.__empty_marker)
        if value is not self.__empty_marker:
            return self.data[name]

        # Field lookup on the instance
        field = self.get_field(name)
        if field is None:
            # expose non-private members of the instance to have access to e.g.
            # self.absolute_url()
            if not name.startswith("_") or not name.startswith("__"):
                return getattr(self.instance, name, default)
            return default

        # Retrieve field value by accessor
        accessor = field.getAccessor(self.instance)
        accessor_name = accessor.__name__

        # Metadata lookup by accessor name
        value = getattr(self.brain, accessor_name, self.__empty_marker)
        if value is self.__empty_marker:
            logger.info("Add metadata column '{}' to the catalog '{}' "
                        "to increase performance!"
                        .format(accessor_name, self.catalog.__name__))
            value = accessor()

        # Process value for publication
        value = self.process_value(value)

        # Store value in the internal data dict
        self.data[name] = value

        return value

    def process_value(self, value):
        """Process publication value
        """
        # UID -> PublicationObject
        if self.is_uid(value):
            return self.get_publish_adapter_for_uid(value)
        # Content -> PublicationObject
        elif api.is_object(value):
            return self.get_publish_adapter_for_uid(api.get_uid(value))
        # DateTime -> DateTime
        elif isinstance(value, DateTime):
            return value
        # Process list values
        elif isinstance(value, (LazyMap, list, tuple)):
            return map(self.process_value, value)
        # Process dict values
        elif isinstance(value, (dict)):
            return {k: self.process_value(v) for k, v in value.iteritems()}
        # Process function
        elif callable(value):
            return self.process_value(value())
        # Always return the unprocessed value last
        return value

    @property
    def uid(self):
        """UID of the wrapped object
        """
        return self._uid

    @property
    def instance(self):
        """Content instance of the wrapped object
        """
        if self._instance is None:
            logger.debug("PublicationObject::instance: *Wakup object*")
            self._instance = api.get_object(self.brain)
        return self._instance

    @property
    def brain(self):
        """Catalog brain of the wrapped object
        """
        if self._brain is None:
            logger.debug("PublicationObject::brain: *Fetch catalog brain*")
            self._brain = self.get_brain_by_uid(self.uid)
            # refetch the brain with the correct catalog
            results = self.catalog({"UID": self.uid})
            if results and len(results) == 1:
                self._brain = results[0]
        return self._brain

    @property
    def catalog(self):
        """Primary registered catalog for the wrapped portal type
        """
        if self._catalog is None:
            logger.debug("PublicationObject::catalog: *Fetch catalog*")
            archetype_tool = api.get_tool("archetype_tool")
            portal_type = self.brain.portal_type
            catalogs = archetype_tool.getCatalogsByType(portal_type)
            if catalogs is None:
                logger.warn("No registered catalog found for portal_type={}"
                            .format(portal_type))
                return api.get_tool("uid_catalog")
            self._catalog = catalogs[0]
        return self._catalog

    @property
    def workflows(self):
        """Return a list of assigned workflows
        """
        wf_ids = api.get_workflows_for(self.instance)
        return map(self.get_workflow_info_for, wf_ids)

    def get_workflow_info_for(self, wf_id):
        """Return a workflow info object
        """
        wf_tool = api.get_tool("portal_workflow")
        # `DCWorkflowDefinition` instance
        workflow = wf_tool.getWorkflowById(wf_id)
        # the state variable, e.g. review_state
        state_var = workflow.state_var
        # tuple of possible transitions
        transitions = wf_tool.getTransitionsFor(self.instance)
        # review history tuple, e.g. ({'action': 'publish', ...}, )
        history = wf_tool.getHistoryOf(wf_id, self.instance)
        # reverse the history
        review_history = history[::-1]
        # the most current history info
        current_state = review_history[0]
        # extracted status id
        status = current_state[state_var]
        # `StateDefinition` instance
        state_definition = workflow.states[status]
        # status title, e.g. "Published"
        status_title = state_definition.title

        # return selected workflow information for the wrapped instance
        return {
            "id": wf_id,
            "status": status,
            "status_title": status_title,
            "state_var": state_var,
            "transitions": transitions,
            "review_history": review_history,
        }

    def get_brain_by_uid(self, uid):
        """Lookup brain in the UID catalog
        """
        if uid == "0":
            return api.get_portal()
        uid_catalog = api.get_tool("uid_catalog")
        results = uid_catalog({"UID": uid})
        if len(results) != 1:
            raise ValueError("Failed to get brain by UID")
        return results[0]

    def get_publish_adapter_for_uid(self, uid):
        """Return a IPublicationObject adapter for the given UID
        """
        brain = self.get_brain_by_uid(uid)
        portal_type = brain.portal_type
        adapter = queryAdapter(uid, IPublicationObject, name=portal_type)
        if adapter is None:
            return PublicationObject(uid)
        return adapter

    def is_valid(self):
        """Self-check
        """
        try:
            self.brain
        except ValueError:
            return False
        return True

    def is_uid(self, uid):
        """Check valid UID format
        """
        if not isinstance(uid, basestring):
            return False
        if len(uid) != 32:
            return False
        if not uid.isalnum():
            return False
        return True

    def stringify(self, value):
        """Convert value to string
        """
        # PublicationObject -> UID
        if IPublicationObject.providedBy(value):
            return str(value)
        # DateTime -> ISO8601 format
        elif isinstance(value, (DateTime)):
            return value.ISO8601()
        # Dict -> convert_value_to_string
        elif isinstance(value, dict):
            return {k: self.stringify(v) for k, v in value.iteritems()}
        # List -> convert_value_to_string
        if isinstance(value, (list, tuple, LazyMap)):
            return map(self.stringify, value)
        return str(value)

    def to_dict(self, converter=None):
        """Returns a copy dict of the current object

        If a converter function is given, pass each value to it.
        Per default the values are converted by `self.stringify`.
        """
        if converter is None:
            converter = self.stringify
        out = dict()
        for k, v in self.iteritems():
            out[k] = converter(v)
        return out

    def to_json(self):
        """Returns a JSON representation of the current object
        """
        return json.dumps(self.to_dict())


class PrintView(BrowserView):
    """Print View
    """
    implements(IPrintView)
    template = ViewPageTemplateFile("templates/printview.pt")

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.uids = self.request.get("items", "").split(",")
        self.objs = map(lambda uid: PublicationObject(uid), self.uids)
        return self.template()

    def render_reports(self):
        template = ViewPageTemplateFile("templates/reports/default.pt")

        rendered_reports = []
        for obj in self.objs:
            # keywords are accessible in "options" in the template
            report = template(
                self, publication_object=obj, **self.get_template_options())
            rendered_reports.append(report)
        return "".join(rendered_reports)

    def get_template_options(self):
        """Returns a mapping object to be passed to the template.

        This data will be accessible in the template in `options`, e.g.:

        <div tal:define='portal options/portal'> ... </div>
        """
        portal = api.get_portal()
        setup = portal.bika_setup
        laboratory = setup.laboratory
        context = {
            "portal": PublicationObject("0"),
            "setup": PublicationObject(api.get_uid(setup)),
            "laboratory": PublicationObject(api.get_uid(laboratory)),
        }
        return context

    def get_paperformats(self):
        """Returns a mapping of available paper formats
        """
        # Todo: Implement cascading lookup: client->registry->config
        return PAPERFORMATS

    def get_image_resource(self, name, prefix="bika.lims.images"):
        """Return the full image resouce URL
        """
        portal = api.get_portal()
        portal_url = portal.absolute_url()

        if not prefix:
            return "{}/{}".format(portal_url, name)
        return "{}/++resource++{}/{}".format(portal_url, prefix, name)

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


class ajaxPrintView(PrintView):
    """Print View with Ajax exposed methods
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(ajaxPrintView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.traverse_subpath = []

    def publishTraverse(self, request, name):
        """Called before __call__ for each path name
        """
        self.traverse_subpath.append(name)
        return self

    @returns_json
    def __call__(self):
        """Dispatch the path to a method and return JSON.
        """
        if len(self.traverse_subpath) < 1:
            return {}

        # check if the method exists
        func_arg = self.traverse_subpath[0]
        func_name = "ajax_{}".format(func_arg)
        func = getattr(self, func_name, None)
        if func is None:
            return self.fail("Invalid function", status=400)

        # Additional provided path segments after the function name are handled
        # as positional arguments
        args = self.traverse_subpath[1:]

        # check mandatory arguments
        func_sig = inspect.getargspec(func)
        # positional arguments after `self` argument
        required_args = func_sig.args[1:]

        if len(args) < len(required_args):
            return self.fail("Wrong signature, please use '{}/{}'"
                             .format(func_arg, "/".join(required_args)), 400)
        return func(*args)

    def fail(self, message, status=500, **kw):
        """Set a JSON error object and a status to the response
        """
        self.request.response.setStatus(status)
        result = {"success": False, "errors": message, "status": status}
        result.update(kw)
        return result

    def pick(self, dct, *keys, **kw):
        """Returns a copy of the dictionary filtered to only have values for the
        whitelisted keys (or list of valid keys)

        >>> pick({"name": "moe", "age": 50, "userid": "moe1"}, "name", "age")
        {'age': 50, 'name': 'moe'}
        """
        copy = dict()
        keys = keys and keys or dct.keys()
        converter = kw.get("converter")

        for key in keys:
            if key in dct.keys():
                copy[key] = self.convert(dct[key], converter)
        return copy

    def convert(self, value, converter):
        """Converts a value with a given converter function.
        """
        if not callable(converter):
            return value
        return converter(value)

    def ajax_get(self, uid, *args, **kwargs):
        """Return the JSONified

        Any additional positional parameter in *args will pick only these keys
        from the returned dictionary.
        """
        logger.info("ajaxPrintView::ajax_get_uid:UID={} args={}"
                    .format(uid, args))

        wrapped = PublicationObject(uid)
        if not wrapped.is_valid():
            return self.fail("No object found for UID '{}'"
                             .format(uid), status=404)

        def converter(value):
            return wrapped.stringify(value)

        return self.pick(wrapped, converter=converter, *args)

    def ajax_paperformats(self, *args):
        """Returns the paperformats

        Any additional positional parameter in *args will pick only these keys
        from the returned dictionary.
        """
        return self.pick(self.get_paperformats(), *args)
