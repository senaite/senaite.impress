# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import json

from DateTime import DateTime
from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFPlone.utils import safe_unicode
from Products.ZCatalog.Lazy import LazyMap
from senaite import api
from senaite.impress import logger
from senaite.impress.decorators import returns_report_model
from senaite.impress.interfaces import IReportModel
from zope.interface import implements


class ReportModel(object):
    """Generic wrapper for content objects

    This wrapper exposes the schema fields of the wrapped content object as
    attributes. The schema field values are looked up by their accessors.

    If the primary catalog of the wrapped object contains a metadata column
    with the same name as the accessor, the metadata colum value is used
    instead.

    Note: Adapter lookup is done by `portal_type` name, e.g.:

    >>> portal_type = api.get_portal_type(self.context)
    >>> adapter = queryAdapter(uid, IReportModel, name=portal_type)
    """
    implements(IReportModel)

    def __init__(self, uid):
        logger.debug("ReportModel({})".format(uid))

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

    def __eq__(self, other):
        return self.uid == other.uid

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

        # Return the value immediately
        if value is not self.__empty_marker:
            return self.data[name]

        # Field lookup on the instance
        field = self.get_field(name)

        if field is None:
            # expose non-private members of the instance/brain to have access
            # to e.g. self.absolute_url (function object) or self.review_state
            if not name.startswith("_") or not name.startswith("__"):
                # check if the instance contains this attribute
                instance = self.instance
                instance_value = getattr(instance, name, self.__empty_marker)
                if instance_value is not self.__empty_marker:
                    return instance_value

                # check if the brain contains this attribute
                brain = self.brain
                brain_value = getattr(brain, name, self.__empty_marker)
                if brain_value is not self.__empty_marker:
                    return brain_value

            return default
        else:
            # Retrieve field value by accessor
            accessor = field.getAccessor(self.instance)
            accessor_name = accessor.__name__

            # Metadata lookup by accessor name
            value = getattr(self.brain, accessor_name, self.__empty_marker)
            if value is self.__empty_marker:
                logger.debug("Add metadata column '{}' to the catalog '{}' "
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
        # UID -> ReportModel
        if api.is_uid(value):
            return self.to_report_model(value)
        # Content -> ReportModel
        elif api.is_object(value):
            return self.to_report_model(value)
        # String -> Unicode
        elif isinstance(value, basestring):
            return safe_unicode(value)
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
        elif safe_callable(value):
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
            logger.debug("ReportModel::instance: *Wakup object*")
            self._instance = api.get_object(self.brain)
        return self._instance

    @property
    def brain(self):
        """Catalog brain of the wrapped object
        """
        if self._brain is None:
            logger.debug("ReportModel::brain: *Fetch catalog brain*")
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
            logger.debug("ReportModel::catalog: *Fetch catalog*")
            archetype_tool = api.get_tool("archetype_tool")
            portal_type = self.brain.portal_type
            catalogs = archetype_tool.getCatalogsByType(portal_type)
            if catalogs is None:
                logger.warn("No registered catalog found for portal_type={}"
                            .format(portal_type))
                return api.get_tool("uid_catalog")
            self._catalog = catalogs[0]
        return self._catalog

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

    @returns_report_model
    def to_report_model(self, thing):
        """Wraps an object into a Report Model
        """
        if api.is_uid(thing):
            return self.get_brain_by_uid(thing)
        if not api.is_object(thing):
            raise TypeError("Expected a portal object, got '{}'"
                            .format(type(thing)))
        return thing

    def is_valid(self):
        """Self-check
        """
        try:
            self.brain
        except ValueError:
            return False
        return True

    def stringify(self, value):
        """Convert value to string

        This method is used to generate a simple JSON representation of the
        object (without dereferencing objects etc.)
        """
        # ReportModel -> UID
        if IReportModel.providedBy(value):
            return str(value)
        # DateTime -> ISO8601 format
        elif isinstance(value, (DateTime)):
            return value.ISO8601()
        # Image/Files -> filename
        elif safe_hasattr(value, "filename"):
            return value.filename
        # Dict -> convert_value_to_string
        elif isinstance(value, dict):
            return {k: self.stringify(v) for k, v in value.iteritems()}
        # List -> convert_value_to_string
        if isinstance(value, (list, tuple, LazyMap)):
            return map(self.stringify, value)
        # Callables
        elif safe_callable(value):
            return self.stringify(value())
        elif isinstance(value, unicode):
            value = value.encode("utf8")
        try:
            return str(value)
        except (AttributeError, TypeError, ValueError):
            logger.warn("Could not convert {} to string".format(repr(value)))
            return None

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
