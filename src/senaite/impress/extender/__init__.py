# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from archetypes.schemaextender.field import ExtensionField
from bika.lims.browser.fields import UIDReferenceField
from Products.ATExtensions.ateapi import RecordField


class ExtRecordField(ExtensionField, RecordField):
    """Holds a dictionary like object
    """


class ExtUIDReferenceField(ExtensionField, UIDReferenceField):
    """Holds a UID reference to an object
    """
