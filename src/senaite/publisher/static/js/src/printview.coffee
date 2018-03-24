import $ from 'jquery'
import jQuery from 'jquery'


class ReportView

  constructor: ->
    console.debug "ReportView::constructor"
    @preview = $("#preview")
    base_url = document.URL.split('printview')[0]
    @url = "#{base_url}/ajax_printview/load_preview"
    return @

  flush: =>
    ###
     * Flush the preview panel
    ###
    @preview.fadeOut 500, ->
      $(@).empty()

  load: (options) =>
    ###
     * Return all report elements
    ###

    params = location.search.substring(1)

    $.ajax
      url: @url + "?#{params}"
      method: 'POST'
      data: options
      context: @
    .done (data) ->
      @preview.append data
      @preview.fadeIn()

  render: (options) =>
    ###
     * Render all reports
    ###
    console.debug "ReportView:render"
    @flush()

    options ?= {}
    options.orientation ?= "portrait"
    options.format ?= "A4"
    options.merge ?= false

    cls = "report #{options.format} #{options.orientation}"
    reports = $(".report")
    reports.removeClass()
    reports.addClass cls

    options["html"] = $("#reports").html()
    @load options


$(document).ready ($) ->
  console.debug '*** SENAITE.PUBLISHER.PRINTVIEW Ready'

  window.report_view = new ReportView()
  window.report_view.render()


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
