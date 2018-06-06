# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from senaite.impress import config
from senaite.impress import senaiteMessageFactory as _
from senaite.impress.interfaces import ITemplateFinder
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class TemplateVocabulary(object):
    def __call__(self, context):
        finder = getUtility(ITemplateFinder)
        templates = finder.get_templates()
        items = [SimpleTerm(t[0], t[0], t[0]) for t in templates]
        return SimpleVocabulary(items)

TemplateVocabularyFactory = TemplateVocabulary()  # noqa


@implementer(IVocabularyFactory)
class PaperformatVocabulary(object):
    def __call__(self, context):
        # XXX make paperformats configurable
        items = []
        for k, v in config.PAPERFORMATS.items():
            title = "{} {}x{}mm".format(k, v["page_width"], v["page_height"])
            items.append(SimpleTerm(k, v, title))
        return SimpleVocabulary(items)

PaperformatVocabularyFactory = PaperformatVocabulary()  # noqa


@implementer(IVocabularyFactory)
class OrientationVocabulary(object):
    def __call__(self, context):
        items = []
        for format in ["portrait", "landscape"]:
            items.append(SimpleTerm(format, format, _(format)))
        return SimpleVocabulary(items)

OrientationVocabularyFactory = OrientationVocabulary()  # noqa
