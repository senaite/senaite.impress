2.3.0 (2022-10-03)
------------------

- #124 Fix mixed sorted PoC groups depending on the sample analyses


2.2.0 (2022-06-10)
------------------

- #119 Simplified report creation API
- #117 Allow to filter selectable impress templates
- #115 ISO17025: Added method title to reports


2.1.0 (2022-01-05)
------------------

- Updated JS/CSS resources
- #114 Pin pyphen to version 0.11.0 to support Python2
- #111 Pin Beautiful Soup version to 4.9.3 to support Python2


2.0.0 (2021-07-26)
------------------

- #108 Fix duplicate metadata in single reports


2.0.0rc3 (2021-01-04)
---------------------

- Updated resources
- Updated build system to Webpack 5
- #103 Fix remarks rendering in reports
- #101 Fix Traceback for CCEmails rendering in publish view


2.0.0rc2 (2020-10-13)
---------------------

- Updated resources


2.0.0rc1 (2020-08-05)
---------------------

- Compatibility with `senaite.core` 2.x


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
