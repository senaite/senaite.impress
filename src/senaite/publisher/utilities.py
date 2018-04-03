# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

import os

from plone.resource.utils import iterDirectoriesOfType
from senaite.publisher import logger


class TemplateFinder(object):
    """Utility to find registered template resources
    """
    def __init__(self, type="senaite.publisher.reports"):
        logger.info("TemplateFinder::init:type={}".format(type))
        self.type = type

    @property
    def resources(self):
        out = []
        for resource in iterDirectoriesOfType(self.type):
            out.append({
                "name": resource.__name__,
                "path": resource.directory,
                "contents": resource.listDirectory(),
            })
        return out

    def get_templates(self, extensions=[".pt", ".html"]):
        templates = []
        for resource in self.resources:
            name = resource["name"]
            path = resource["path"]
            contents = resource["contents"] or []
            for content in contents:
                basename, ext = os.path.splitext(content)
                if ext not in extensions:
                    continue
                template = content
                if name:
                    template = u"{}:{}".format(name, content)
                template_path = os.path.join(path, content)
                templates.append((template, template_path))
        return templates
