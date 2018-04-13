# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.PUBLISHER
#
# Copyright 2018 by it's authors.

from senaite.publisher.interfaces import ITemplateFinder
from zope.component import getUtility
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class TemplatesVocabulary(object):
    def __call__(self, context):
        finder = getUtility(ITemplateFinder)
        templates = finder.get_templates()
        items = [SimpleTerm(t[0], t[0], t[0]) for t in templates]
        return SimpleVocabulary(items)

TemplatesVocabularyFactory = TemplatesVocabulary()  # noqa
