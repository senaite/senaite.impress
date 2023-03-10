# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS.
#
# SENAITE.IMPRESS is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2023 by it's authors.
# Some rights reserved, see README and LICENSE.

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
