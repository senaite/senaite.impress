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
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims import api
from bika.lims.permissions import ManageBika
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class SetupButtonViewlet(ViewletBase):
    """Viewlet that shows the setup selector
    """
    index = ViewPageTemplateFile("templates/setupbutton.pt")

    def __init__(self, context, request, view, manager=None):
        super(SetupButtonViewlet, self).__init__(
            context, request, view, manager=manager)
        self.context = context
        self.request = request
        self.view = view

    @property
    def portal(self):
        """Return the portal object
        """
        return api.get_portal()

    @property
    def user(self):
        return api.get_current_user()

    def is_manager(self):
        """Checks if the current user has manager rights
        """
        roles = api.get_roles_for_permission(ManageBika, self.context)
        return self.user.has_role(roles)
