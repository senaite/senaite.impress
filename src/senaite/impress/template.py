# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

import os

from pkg_resources import resource_filename

from plone.resource.utils import iterDirectoriesOfType
from senaite.impress import logger

DEFAULT_TEMPLATE = "Default.pt"


class TemplateFinder(object):
    """Utility to find registered template resources
    """
    def __init__(self, type="senaite.impress.reports"):
        logger.info("TemplateFinder::init:type={}".format(type))
        self.type = type

    def __call__(self):
        return self.get_templates()

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

    @property
    def default_template(self):
        path = os.path.join("templates", "reports", DEFAULT_TEMPLATE)
        return resource_filename("senaite.impress", path)

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
                if basename.lower().startswith("example"):
                    continue
                template = content
                if name:
                    template = u"{}:{}".format(name, content)
                template_path = os.path.join(path, content)
                templates.append((template, template_path))
        return templates

    def find_template(self, name):
        """Returns the template path by name
        """
        templates = dict(self.get_templates())
        return templates.get(name)
