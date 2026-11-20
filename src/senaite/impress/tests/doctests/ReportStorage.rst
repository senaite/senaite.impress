Report Storage
--------------

The storage adapter stores a generated PDF as a `ResultsReport`. A
multi-report is stored once, inside its primary sample, and references all
contained samples.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ReportStorage

Test Setup
..........

Needed Imports:

    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from senaite.core.catalog import REPORT_CATALOG
    >>> from senaite.impress.storage import PdfReportStorageAdapter

Variables:

    >>> portal = api.get_portal()
    >>> request = self.request
    >>> bikasetup = api.get_bika_setup()
    >>> setup = api.get_senaite_setup()

Helpers:

    >>> def new_sample():
    ...     values = {
    ...         "Client": api.get_uid(client),
    ...         "Contact": api.get_uid(contact),
    ...         "DateSampled": DateTime().strftime("%Y-%m-%d"),
    ...         "SampleType": api.get_uid(sampletype),
    ...     }
    ...     return create_analysisrequest(
    ...         client, request, values, [api.get_uid(service)])

    >>> def get_report_ids(sample):
    ...     return map(api.get_id, sample.getReports())

LIMS Setup:

    >>> setRoles(portal, TEST_USER_ID, ["LabManager"])
    >>> client = api.create(portal.clients, "Client", Name="Happy Hills", ClientID="HH")
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.sampletypes, "SampleType", title="Water", Prefix="W")
    >>> labcontact = api.create(bikasetup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.departments, "Department", title="Chemistry", Manager=labcontact)
    >>> category = api.create(setup.analysiscategories, "AnalysisCategory", title="Metals", Department=department)
    >>> service = api.create(bikasetup.bika_analysisservices, "AnalysisService", title="Copper", Keyword="Cu", Category=category.UID())


Store a multi-report
....................

Create two samples and store a multi-report that contains both:

    >>> sample1 = new_sample()
    >>> sample2 = new_sample()
    >>> uids = map(api.get_uid, [sample1, sample2])

    >>> storage = PdfReportStorageAdapter(portal, request)
    >>> reports = storage.store("%PDF-1.4", "<html/>", uids)

The PDF is stored once, inside the primary sample, which is the most recent
one:

    >>> len(reports)
    1
    >>> report = reports[0]
    >>> api.get_parent(report) == sample2
    True
    >>> report.getContainedSamples() == [sample1, sample2]
    True

Both samples list the report:

    >>> get_report_ids(sample1) == [api.get_id(report)]
    True
    >>> get_report_ids(sample2) == [api.get_id(report)]
    True

The report catalog finds it for each contained sample, which is the query of
the published results listing of a sample:

    >>> catalog = api.get_tool(REPORT_CATALOG)
    >>> len(catalog(portal_type="ResultsReport", sample_uid=uids[0]))
    1
    >>> len(catalog(portal_type="ResultsReport", sample_uid=uids[1]))
    1


Registry
........

The setting to store multi-reports individually is gone:

    >>> key = "senaite.impress.store_multireports_individually"
    >>> api.get_registry_record(key) is None
    True

The upgrade step removes the record of existing sites:

    >>> from plone.registry import field
    >>> from plone.registry import Record
    >>> from plone.registry.interfaces import IRegistry
    >>> from senaite.impress.upgrades.v02_07_000 import remove_store_individually_registry
    >>> from zope.component import getUtility

    >>> registry = getUtility(IRegistry)
    >>> registry.records[key] = Record(field.Bool(), True)
    >>> api.get_registry_record(key)
    True

    >>> remove_store_individually_registry(portal.portal_setup)
    >>> key in registry.records
    False
