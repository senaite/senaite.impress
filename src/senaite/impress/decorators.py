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

import json
import threading
import time
from functools import wraps

from bika.lims import api
from senaite.core.supermodel.interfaces import ISuperModel
from senaite.impress import logger
from zope.component import queryAdapter


def synchronized(max_connections=2, verbose=0):
    """Synchronize function call via semaphore
    """
    semaphore = threading.BoundedSemaphore(max_connections, verbose=verbose)

    def inner(func):
        logger.debug("Semaphore for {} -> {}".format(func, semaphore))
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info("==> {}::Acquire Semaphore ...".format(
                    func.__name__))
                semaphore.acquire()
                return func(*args, **kwargs)
            finally:
                logger.info("<== {}::Release Semaphore ...".format(
                    func.__name__))
                semaphore.release()

        return wrapper
    return inner


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


def returns_super_model(func):
    """Wraps an object into a super model
    """

    def to_super_model(obj):
        # avoid circular imports
        from senaite.core.supermodel import SuperModel

        # Object is already a SuperModel, return immediately
        if isinstance(obj, SuperModel):
            return obj

        # Only portal objects are supported
        if not api.is_object(obj):
            return None

        # Wrap the object into a specific Publication Object Adapter
        uid = api.get_uid(obj)
        portal_type = api.get_portal_type(obj)

        adapter = queryAdapter(uid, ISuperModel, name=portal_type)
        if adapter is None:
            return SuperModel(uid)
        return adapter

    def decorator(*args, **kwargs):
        obj = func(*args, **kwargs)
        if isinstance(obj, (list, tuple)):
            return filter(None, map(to_super_model, obj))
        return to_super_model(obj)

    return decorator


def timeit(threshold=0):
    """Decorator to log the execution time of a function
    """

    def inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            return_value = func(*args, **kwargs)
            end = time.time()
            duration = float(end-start)
            if duration > threshold:
                logger.info("Execution of '{}{}' took {:2f}s".format(
                    func.__name__, args, duration))
            return return_value
        return wrapper
    return inner
