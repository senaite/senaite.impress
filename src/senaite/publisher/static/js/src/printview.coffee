import $ from 'jquery'
import jQuery from 'jquery'


class ReportView

  constructor: ->
    console.debug "ReportView::constructor"
    @preview = $("#preview")
    @reports = $("#reports")

    base_url = document.URL.split('printview')[0]
    @url = "#{base_url}/ajax_printview/load_preview"
    return @

  get_reports: =>
    ###
     * Return all report elements
    ###
    return $(".report", @reports)

  flush_preview: =>
    ###
     * Flush the preview panel
    ###
    @preview.empty()

  load_report_preview: (html) =>
    ###
     * Return all report elements
    ###

    console.debug "loadig report"
    $.ajax
      url: @url
      async: no  # weasyprint `render` hangs w/o this...
      method: 'POST'
      data:
        html: html
      context: @
    .done (data) ->
      console.debug "GOT DATA"
      @preview.append data
      @preview.fadeIn()

  render: =>
    ###
     * Render all reports
    ###
    reports = @get_reports()
    console.debug "ReportView:render: #{reports.length} reports"

    me = this
    reports.each (index, report) ->
      html = report.outerHTML
      me.load_report_preview html

    # @load_report_preview @reports.html()



$(document).ready ($) ->
  console.debug '*** SENAITE.PUBLISHER.PRINTVIEW Ready'

  report_view = new ReportView()
  report_view.render()


#document.addEventListener("DOMContentLoaded", function() {
#
#  console.debug("DOM Content Loaded")
#
#  const html = document.getElementById("publisher")
#  const url = document.URL.split("printview")[0] + "ajax_printview/process_html"
#
#  fetch(url, {
#    method: "POST",
#    body: {
#      html: html
#    }
#  }).then((data) => {
#
#      debugger
#  })
#
#
#});
# */
#
#import React from 'react';
#import ReactDOM from 'react-dom';
#
#const container = document.getElementById('container');
#
#const app = (
#    <div>
#        <h1>JSX</h1>
#        <span>My first JSX span!</span>
#    </div>
#);
#ReactDOM.render(app, container); */
