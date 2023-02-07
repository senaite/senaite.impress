# -*- coding: utf-8 -*-
from zope.viewlet.interfaces import IViewletManager


class IPublishHtmlHeadViewlets(IViewletManager):
    """A viewlet manager that sits inside the <head> of the publish view
    """


class IPublishCustomHtmlHeadViewlets(IViewletManager):
    """A viewlet manager that comes after the main html head viewlets
    """


class IPublishTopViewlets(IViewletManager):
    """A viewlet manager at the top of the publish view
    """


class IPublishContentViewlets(IViewletManager):
    """A viewlet manager in the publish view above the publish controls
    """
