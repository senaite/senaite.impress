# -*- coding: utf-8 -*-

from bika.lims import api
from DateTime import DateTime
from senaite.impress.interfaces import IReportWrapper
from zope.interface import implementer


@implementer(IReportWrapper)
class ReportWrapper(object):
    """Report wrapper to generate PDF
    """
    def __init__(self,
                 html,
                 collection,
                 template,
                 paperformat,
                 orientation,
                 report_options,
                 publisher):

        self._pdf = None
        self.html = html
        self.collection = collection
        self.template = template
        self.paperformat = paperformat
        self.orientation = orientation
        self.report_options = report_options
        self.publisher = publisher
        self.created = DateTime()

    @property
    def pdf(self):
        """Returns or generates the PDF on the fly
        """
        if self._pdf is None:
            self._pdf = self.publisher.write_pdf(self.html)
        return self._pdf

    def get_metadata(self, **kw):
        """Returns the report metadata as a dictionary
        """
        metadata = {
            "template": self.template,
            "paperformat": self.paperformat,
            "orientation": self.orientation,
            "timestamp": self.created.ISO(),
        }
        metadata.update(kw)
        return metadata

    def get_uids(self):
        """Returns the UIDs of the collection
        """
        return list(map(api.get_uid, self.collection))

    def get_ids(self):
        """Returns the IDs of the collection
        """
        return list(map(api.get_id, self.collection))

    def __repr__(self):
        return "<ReportWrapper for %s>" % ",".join(self.get_ids())
