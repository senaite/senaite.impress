Custom Paper Formats
--------------------

Custom paper formats can be defined via the impress control panel.
They are merged with built-in formats and can be mapped to specific
report templates for automatic format selection.

Running this test from the buildout directory:

    bin/test test_textual_doctests -t CustomPaperFormats

Test Setup
..........

Needed Imports

    >>> from collections import OrderedDict
    >>> from senaite.impress.config import PAPERFORMATS


Built-in paper formats
......................

The built-in PAPERFORMATS dict contains standard formats:

    >>> "A4" in PAPERFORMATS
    True

    >>> "A3" in PAPERFORMATS
    True

    >>> PAPERFORMATS["A4"]["page_width"]
    210.0

    >>> PAPERFORMATS["A4"]["page_height"]
    297.0

    >>> PAPERFORMATS["A4"]["margin_top"]
    20.0


ReportView provides get_page_margins
.....................................

The base ReportView provides an overridable get_page_margins
method that returns an empty dict by default:

    >>> from senaite.impress.reportview import ReportView

    >>> hasattr(ReportView, "get_page_margins")
    True


Interface declarations
......................

Both IReportView and IMultiReportView declare get_page_margins:

    >>> from senaite.impress.interfaces import IReportView
    >>> from senaite.impress.interfaces import IMultiReportView

    >>> "get_page_margins" in IReportView.names()
    True

    >>> "get_page_margins" in IMultiReportView.names()
    True


Control panel interfaces
........................

The IPaperFormat row schema defines all required fields:

    >>> from senaite.impress.controlpanel import IPaperFormat
    >>> sorted(IPaperFormat.names())
    ['key', 'margin_bottom', 'margin_left', 'margin_right', 'margin_top', 'page_height', 'page_width', 'title']

The ITemplateFormatMapping row schema has template and format:

    >>> from senaite.impress.controlpanel import ITemplateFormatMapping
    >>> sorted(ITemplateFormatMapping.names())
    ['format', 'template']


Vocabulary includes built-in formats
.....................................

The PaperformatVocabulary should include built-in formats:

    >>> from senaite.impress.vocabularies import PaperformatVocabulary
    >>> vocab_factory = PaperformatVocabulary()

The vocabulary factory is callable:

    >>> callable(vocab_factory)
    True
