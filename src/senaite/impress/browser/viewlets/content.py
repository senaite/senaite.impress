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

    @property
    def publishview(self):
        return api.get_view(
            "publish", context=self.context, request=self.request)

    def get_uids(self):
        """Parse the UIDs from the request `items` parameter
        """
        return self.publishview.get_uids()

    def get_collection(self, uids, group_by=None):
        """Wraps the given UIDs into a collection of SuperModels
        """
        return self.publishview.get_collection(uids, group_by=group_by)
