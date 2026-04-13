Report Logo
-----------

The report logo feature allows uploading a custom logo via the
impress control panel. The logo is served through a dedicated view
and used in report headers with a fallback to the default SENAITE logo.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t ReportLogo

Test Setup
..........

Needed Imports

    >>> from senaite.impress.reportview import ReportView
    >>> from senaite.impress.reportview import DEFAULT_LOGO


Default Logo URL
................

The default logo constant points to the SENAITE SVG:

    >>> DEFAULT_LOGO
    '++plone++senaite.core.static/images/senaite.svg'


ReportView base class
.....................

The base ReportView provides the get_report_logo_url method:

    >>> hasattr(ReportView, "get_report_logo_url")
    True


ReportLogo view
...............

The ReportLogo view serves uploaded logos from the registry:

    >>> from senaite.impress.reportlogo import ReportLogo

    >>> hasattr(ReportLogo, "_getFile")
    True

    >>> hasattr(ReportLogo, "__call__")
    True


Interface declarations
......................

The IReportView and IMultiReportView interfaces declare the
get_report_logo_url method:

    >>> from senaite.impress.interfaces import IReportView
    >>> from senaite.impress.interfaces import IMultiReportView

    >>> "get_report_logo_url" in IReportView.names()
    True

    >>> "get_report_logo_url" in IMultiReportView.names()
    True
