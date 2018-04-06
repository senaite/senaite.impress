# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.LIMS
#
# Copyright 2018 by it's authors.
# Some rights reserved. See LICENSE and CONTRIBUTING.

from string import Template

from senaite.publisher import logger
from senaite.publisher.interfaces import IMultiReportView
from zope.globalrequest import getRequest
from zope.interface import implements


TEMPLATE = Template("""<!-- Multi Report Template ${id} -->
<div class="report" id="${id}" uid="${uid}">
  <script type="text/javascript">
    console.log("*** BEFORE TEMPLATE RENDER ${id} ***");
  </script>
  ${template}
</div>
""")


class MultiReportView(object):
    implements(IMultiReportView)

    def __init__(self, collection):
        logger.info("MultiReportView::__init__:collection={}"
                    .format(collection))
        self.collection = collection
        self.context = collection
        self.request = getRequest()

    def render(self, template):
        context = self.get_template_context(self.collection)
        template = Template(template).safe_substitute(context)
        return TEMPLATE.safe_substitute(context, template=template)

    def get_template_context(self, collection):
        uids = map(lambda model: model.UID(), collection)
        return {
            "id": "multireport",
            "uid": ",".join(uids),
        }
