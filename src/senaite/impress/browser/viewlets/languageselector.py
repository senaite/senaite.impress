# -*- coding: utf-8 -*-

from plone.app.i18n.locales.browser.selector import LanguageSelector
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class LanguageSelectorViewlet(ViewletBase):
    """Viewlet that shows the language selector
    """
    index = ViewPageTemplateFile("templates/languageselector.pt")

    def __init__(self, context, request, view, manager=None):
        super(LanguageSelectorViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def get_language_info(self):
        """Returns the current configured languages
        """

        # Use the language selector viewlet
        viewlet = LanguageSelector(self.context, self.request, None, None)
        viewlet.update()

        return {
            "available": viewlet.available(),
            "languages": viewlet.languages(),
        }
