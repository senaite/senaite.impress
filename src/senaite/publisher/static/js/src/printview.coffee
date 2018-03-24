import $ from 'jquery'
import jQuery from 'jquery'


class ReportView

  constructor: ->
    console.debug "ReportView::constructor"
    @preview = $("#preview")
    base_url = document.URL.split('printview')[0]
    @url = "#{base_url}/ajax_printview"
    return @

  load: (options) =>
    ###
     * Return all report elements
    ###


    params = location.search.substring(1)

    $.ajax
      url: @url + "/load_preview?#{params}"
      method: 'POST'
      data: options
      context: @
    .done (data) ->
      if data == ""
        data = "No reports found"
      me = @
      @preview.fadeOut 500, ->
        el = $(@)
        el.empty()
        el.append data
        el.fadeIn()
        me.set_css options

  set_css: (options) =>
    options ?= {}
    options.orientation ?= $("#orientation").val()
    options.format ?= $("#paperformats").val()

    size_cls = "#{options.format} #{options.orientation}"
    report_cls = "report #{size_cls}"

    reports = $(".report")
    reports.removeClass()
    reports.addClass report_cls

    body = $("body")
    body.removeClass()
    body.addClass size_cls

  render: (options) =>
    ###
     * Render all reports
    ###
    console.debug "ReportView:render"

    options ?= {}
    options.orientation ?= $("#orientation").val()
    options.format ?= $("#paperformats").val()
    options.merge ?= false
    @set_css options
    options.html = $("#reports").html()

    return @load(options)


# Document Ready handler
$(document).ready ($) ->
  console.debug '*** SENAITE.PUBLISHER.PRINTVIEW Ready'

  window.report_view = new ReportView()
  window.report_view.render()

  $("#download").on "click", (event) =>
    event.preventDefault()
    form = $("form[name='printform']")
    report_view.set_css()
    html = $("#reports").html()
    $("input[name='html']").val html
    form.submit()

  $("select#orientation").on "change", (event) =>
    console.log "Orientation changed"
    report_view.render()

  $("select#paperformats").on "change", (event) =>
    console.log "Paperformats changed"
    report_view.render()
