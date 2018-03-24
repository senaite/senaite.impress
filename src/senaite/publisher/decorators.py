# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import json
import threading

from senaite.publisher import logger


def synchronized(func, max_connections=1):
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
