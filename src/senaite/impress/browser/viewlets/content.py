# -*- coding: utf-8 -*-

from bika.lims import api
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class PublishContentViewlet(ViewletBase):
    """Viewlet that shows a listing of the selected impress objects
    """
    index = ViewPageTemplateFile("templates/content.pt")

    def __init__(self, context, request, view, manager=None):
        super(PublishContentViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    def get_listing_view(self):
        request = api.get_request()
        view_name = "publish_content_listing"
        view = api.get_view(view_name, context=self.context, request=request)
        return view

    def contents_table(self):
        view = self.get_listing_view()
        view.update()
        view.before_render()
        return view.ajax_contents_table()
