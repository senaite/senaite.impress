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

from collections import OrderedDict

from six.moves import urllib

from bika.lims import api
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import IAnalysisRequest
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for
from bika.lims.utils import t
from senaite.app.listing import ListingView
from senaite.core.api import dtime


class ContentListingView(ListingView):
    """Listing table of selected UIDs
    """
    def __init__(self, context, request):
        super(ContentListingView, self).__init__(context, request)

        self.pagesize = 9999
        self.context_actions = {}
        self.show_search = False
        self.show_select_column = False
        self.show_workflow_action_buttons = False
        self.show_table_footer = False
        self.omit_form = True
        self.allow_row_reorder = True

        # Show categories
        self.categories = []
        self.show_categories = True
        self.expand_all_categories = False

        self.columns = OrderedDict((
            # Although 'created' column is not displayed in the list (see
            # review_states to check the columns that will be rendered), this
            # column is needed to sort the list by create date
            ("id", {
                "title": _("ID"),
                "sortable": False,
                "toggle": True}),
            ("title", {
                "title": _("Title"),
                "sortable": False,
                "toggle": True}),
            ("SampleType", {
                "title": _("Sample Type"),
                "sortable": False,
                "toggle": True}),
            ("SamplePoint", {
                "title": _("Sample Point"),
                "sortable": False,
                "toggle": True}),
            ("created", {
                "title": _("Registered"),
                "sortable": False,
                "toggle": False}),
            ("DateSampled", {
                "title": _("Date Sampled"),
                "sortable": False,
                "toggle": True}),
            ("Client", {
                "title": _("Client"),
                "sortable": False,
                "toggle": True}),
            ("ClientID", {
                "title": _("Client ID"),
                "sortable": False,
                "toggle": True}),
            ("Contact", {
                "title": _("Contact"),
                "sortable": False,
                "toggle": True}),
            ("BatchID", {
                "title": _("Batch ID"),
                "sortable": False,
                "toggle": True}),
            ("review_state", {
                "title": _("Workflow State ID"),
                "sortable": False,
                "toggle": False}),
            ("state", {
                "title": _("Workflow State"),
                "sortable": False,
                "toggle": True}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("All"),
                "contentFilter": {},
                "transitions": [],
                "custom_transitions": [],
                "columns": self.columns.keys()
            }
        ]

    def get_uids(self):
        """Parse the UIDs from the query string

        NOTE:

        This listing view is called asynchronously with a new HTTP POST request
        from senaite.app.listing (see JS: api.get_json)

        Therefore, the original `?items` request parameter is contained only in
        the request QUERY_STRING, but no longer in the form data, because there
        we have only the payload from the POST request

        XXX: This might be better done in senaite.app.listing
        """
        uids = []
        qs = self.request.get_header("query_string", "")
        params = urllib.parse.parse_qs(qs)
        items = params.get("items", [])
        for item in items:
            uids.extend(filter(api.is_uid, item.split(",")))
        return uids

    def make_empty_item(self, **kw):
        """Create a new empty item
        """
        item = {
            "uid": None,
            "before": {},
            "after": {},
            "replace": {},
            "allow_edit": [],
            "disabled": False,
            "state_class": "state-active",
        }
        item.update(**kw)
        return item

    def folderitems(self):
        items = []
        for num, uid in enumerate(self.get_uids()):
            obj = api.get_object(uid)
            # create base folderitem
            item = self.make_empty_item(**{
                "uid": uid,
                "id": api.get_id(obj),
                "title": api.get_title(obj),
                "replace": {
                    "id": get_link_for(obj),
                }
            })

            # append workflow info
            self._folder_item_workflow(obj, item)
            # append sample specific info
            self._folder_item_sample(obj, item)

            items.append(self.folderitem(obj, item, num))

        return items

    def folderitem(self, obj, item, index):
        """Render a row in the listing
        """
        return item

    def _folder_item_workflow(self, obj, item):
        """Add workflow information to the item
        """
        state = "Active"
        review_state = "active"

        wf_tool = api.get_tool("portal_workflow")
        wfs = wf_tool.getWorkflowsFor(obj)

        for wf in wfs:
            review_state = wf.getInfoFor(obj, wf.state_var, "")
            sdef = wf.states.get(review_state)
            state = sdef.title
            break

        item["state"] = t(state)
        item["review_state"] = review_state
        item["state_class"] = "state-{}".format(review_state)

    def _folder_item_sample(self, obj, item):
        """Add sample specific information
        """
        if not IAnalysisRequest.providedBy(obj):
            return
        item["SampleType"] = obj.getSampleTypeTitle()

        # sample point
        sp = obj.getSamplePoint()
        if sp:
            sp_id = api.get_id(sp)
            sp_title = api.get_title(sp)
            sp_url = api.get_url(sp)
            item["SamplePoint"] = api.get_title(sp)
            item["replace"]["SamplePoint"] = get_link(
                sp_url, value=sp_title or sp_id, target="_blank")

        client = obj.getClient()
        client_url = api.get_url(client)
        client_id = client.getClientID()
        client_name = client.getName()

        # Categorize objects by client name
        item["category"] = client_name
        if client_name not in self.categories:
            self.categories.append(client_name)

        # Client Name
        item["Client"] = client_name
        item["replace"]["Client"] = get_link(
            client_url, value=client_name, target="_blank")

        # Client ID
        item["ClientID"] = client.getClientID()
        item["replace"]["ClientID"] = get_link(
            client_url, value=client_id, target="_blank")

        # Client Contact
        contact = obj.getContact()
        if contact:
            contact_url = api.get_url(contact)
            contact_name = contact.getFullname()
            item["Contact"] = contact.getFullname()
            item["replace"]["Contact"] = get_link(
                contact_url, value=contact_name, target="_blank")

        # Date Sampled
        date_created = obj.created()
        date_sampled = obj.getDateSampled()
        item["created"] = dtime.to_localized_time(
            date_created, long_format=True,
            context=self.context, request=self.request)
        item["DateSampled"] = dtime.to_localized_time(
            date_sampled, long_format=True,
            context=self.context, request=self.request)

        # Batch
        batch = obj.getBatch()
        if batch:
            batch_id = batch.getId()
            batch_url = api.get_url(batch)
            item["BatchID"] = batch.getId()
            item["replace"]["BatchID"] = get_link(
                batch_url, value=batch_id, target="_blank")
