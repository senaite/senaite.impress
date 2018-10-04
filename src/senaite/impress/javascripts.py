# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import re

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.PythonScripts.standard import url_quote

INCLUDE = [
    ".*jquery",
    "d3.js",
    "bika.lims.graphics.range.js",
    "senaite.impress.*.js",  # append all senaite.impress javascripts
]


class JavaScriptsView(BrowserView):
    """Helper View to inject uncooked JS from portal_javascripts

    Most of it copied from Products.ResourceRegistries
    https://github.com/plone/Products.ResourceRegistries/blob/master/Products/ResourceRegistries/browser/scripts.pt
    """

    def registry(self):
        return getToolByName(aq_inner(self.context), "portal_javascripts")

    def skinname(self):
        return aq_inner(self.context).getCurrentSkinName()

    def scripts(self):
        registry = self.registry()
        registry_url = registry.absolute_url()
        skinname = url_quote(self.skinname())
        # get the uncooked resources
        scripts = registry.getResources()
        result = []

        for script in scripts:
            # only consider enabled JS resources
            if not script.getEnabled():
                continue
            # Only include JS where the regular expression matches
            script_id = script.getId()
            if not any(map(lambda rx: re.findall(rx, script_id), INCLUDE)):
                continue

            if script.isExternalResource():
                src = "%s" % (script.getId(),)
            else:
                src = "%s/%s/%s" % (registry_url, skinname, script.getId())
            data = {
                "src": src,
            }
            result.append(data)
        return result
