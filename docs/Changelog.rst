1.2.4 (2020-08-05)
------------------

- #96 Remove call to getObjectWorkflowStates (in `is_provisional` func)
- #91 Fix infinite recursion when calling print/publish view w/o items parameter
- #89 PDF Print View
- #88 Support context aware report controller views


1.2.3 (2020-03-01)
------------------

- #86 Allow request parameter overrides for template, orientation and paperformat


1.2.2 (2019-10-26)
------------------

- #83: Handle `None` values in decorator more gracefully
- #82: Fix Date Published is empty on MultiDefault report
- #81: Rebuild JavaScript bundle with new versions
- #80: Update Bootstrap CSS to version 4.3.1
- #79: Use senaite.core.api instead of senaite.api
- #78: Fix template error on missing lab address data


1.2.1 (2019-07-01)
------------------

- #75: Conflict safe concurrent report creation
- #71: Implemented storage adapter
- #73: Extend README wrt 'Reports in external packages'
- #66: Fix Publication Preference Traceback with Default template
- #68: Fix empty Date Published on Default report


1.2.0 (2019-03-30)
------------------

- #64: Fix Rejected AS are shown in the PDF Report
- #62: Better error message handling
- #57: SENAITE CORE integration
- #52: Use the most recent AR as the primary storage
- #48: Fix PDF storage in primary AR when "Store Multi-Report PDFs Individually" option is turned off


1.1.0 (2018-10-04)
------------------

- #44: Changed field ChildAnalysisRequest -> Retest
- #42: Combine Attachments coming from Request and Analysis together for unified grouping/sorting
- #41: Default reports update
- #40: Customizable report options
- #37: Added hyphenize and get_transition_date helper methods
- #36: Allow JS injection and custom report scripts
- #34: Pass through the calculated dimensions to the template
- #33: Include D3JS and support for Range Graphs
- #32: Added language selector
- #31: Fix sort order of uniquified items
- #30: Keep order of grouped items
- #29: Added report developer mode
- #28: Fixed i18n domain for time localization
- #27: Refactored Report Adapters to Multi Adapters
- #25: Added controlpanel descriptions
- #24: Control individual report generation for multi-report PDFs
- #23: Fixed multi client report handling
- #21: Improved email template
- #19: Allow additional attachments in publication email
- #18: Fixed barcode rendering in multi-colum report
- #17: Fix alert section overlapping of the header section
- #16: Fix unicode error in sort method
- #15: Handle commas in recipient email name better
- #13: Fix bootstrap columns CSS for WeasyPrint
- #12: Added upgrade-step machinery
- #11: Refactored to ReportModel -> SuperModel


1.0.2 (2018-07-10)
------------------

- #8: Better Print CSS
- #7: Correct margin calculation
- #6: Updated default report templates


1.0.1 (2018-06-23)
------------------

- Pinned `senaite.api>=1.2.0`
- Updated PyPI page


1.0.0 (2018-06-23)
------------------

- Initial Release
