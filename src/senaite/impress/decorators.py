# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import json
import threading

from senaite import api
from senaite.impress import logger
from senaite.impress.interfaces import IReportModel
from zope.component import queryAdapter


def synchronized(func, max_connections=2):
    """Synchronize function call via semaphore
    """
    semaphore = threading.BoundedSemaphore(max_connections)
    logger.debug("Semaphore for {} -> {}".format(func, semaphore))

    def decorator(*args, **kwargs):
        try:
            logger.info("==> {}::Acquire Semaphore ...".format(
                func.__name__))
            semaphore.acquire()
            return func(*args, **kwargs)
        finally:
            logger.info("<== {}::Release Semaphore ...".format(
                func.__name__))
            semaphore.release()
    return decorator


def returns_json(func):
    """Decorator for functions which return JSON
    """
    def decorator(*args, **kwargs):
        result = func(*args, **kwargs)
        instance = args[0]
        request = getattr(instance, "request", None)
        request.response.setHeader("Content-Type", "application/json")
        return json.dumps(result)
    return decorator


def returns_report_model(func):
    """Wraps an object into a report model
    """

    def to_report_model(obj):
        # avoid circular imports
        from senaite.impress.reportmodel import ReportModel

        # Object is already a Publication Object, return immediately
        if isinstance(obj, ReportModel):
            return obj

        # Only portal objects are supported
        if not api.is_object(obj):
            raise TypeError("Expected a portal object, got '{}'"
                            .format(type(obj)))

        # Wrap the object into a specific Publication Object Adapter
        uid = api.get_uid(obj)
        portal_type = api.get_portal_type(obj)

        adapter = queryAdapter(uid, IReportModel, name=portal_type)
        if adapter is None:
            return ReportModel(uid)
        return adapter

    def decorator(*args, **kwargs):
        obj = func(*args, **kwargs)
        if isinstance(obj, (list, tuple)):
            return map(to_report_model, obj)
        return to_report_model(obj)

    return decorator
