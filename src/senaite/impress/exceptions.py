# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from zope.globalrequest import getRequest


class PublisherError(Exception):
    """Exception Class for Publiser Error
    """


class PublisherAPIError(Exception):
    """Exception Class for Publisher API Errors
    """

    def __init__(self, status, message):
        self.message = message
        self.status = status
        self.setStatus(status)

    def setStatus(self, status):
        request = getRequest()
        request.response.setStatus(status)

    def __str__(self):
        return self.message
