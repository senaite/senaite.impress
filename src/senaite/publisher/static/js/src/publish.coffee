import $ from 'jquery'
import "../vendor/jquery-barcode-2.0.2.js"
window.$ = $


class PublishAPI

  constructor: ->
    console.debug "PublishAPI::constructor"
    @preview = $("#preview")
    base_url = document.URL.split('printview')[0]
    @url = "#{base_url}/ajax_publish"
    return @

  render_barcodes: =>
    $('.barcode').each ->
      id = $(this).attr('data-id')
      console.debug "Render Barcode #{id}"
      code = $(this).attr('data-code')
      barHeight = $(this).attr('data-barHeight')
      addQuietZone = $(this).attr('data-addQuietZone')
      showHRI = $(this).attr('data-showHRI')

      $(this).barcode id, code,
        'barHeight': parseInt(barHeight)
        'addQuietZone': addQuietZone == 'true'
        'showHRI': showHRI == 'true'
        'output': 'bmp'

      if showHRI == 'true'
        # When output is set to "bmp", the showHRI parameter (that
        # prints the ID below the barcode) is dissmissed by barcode.js
        # so we need to add it manually
        $(this).find('.barcode-hri').remove()
        barcode_hri = '<div class=\'barcode-hri\'>' + id + '</div>'
        $(this).append barcode_hri

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
    options.orientation ?= $("[name='orientation']").val()
    options.format ?= $("[name='format']").val()

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
    console.debug "PublishAPI:render"
    @render_barcodes()

    @preview.empty()

    options ?= {}

    options.orientation ?= $("[name='orientation']").val()
    options.format ?= $("[name='format']").val()
    options.merge ?= $("[name='merge']").prop("checked")

    @set_css options
    options.html = $("#reports").html()

    return @load(options)

  reload: (options) =>
    ###
     * Reload the HTML from the server
    ###
    console.debug "PublishAPI:reload"

    options ?= {}
    container = $("#reports")
    container.empty()

    params = location.search.substring(1)

    $.ajax
      url: @url + "/render_reports?#{params}"
      method: 'POST'
      data: options
      context: @
    .done (data) ->
      container.append data
      @render()

# Document Ready handler
$(document).ready ($) ->
  console.debug '*** SENAITE.PUBLISHER.PUBLISH Ready'

  window.publish_api = new PublishAPI()
  window.publish_api.render()

  $("#download").on "click", (event) =>
    event.preventDefault()
    form = $("form[name='publishform']")
    publish_api.set_css()
    html = $("#reports").html()
    $("input[name='html']").val html
    form.submit()

  $("select[name='orientation']").on "change", (event) =>
    console.log "Orientation changed"
    publish_api.render()

  $("select[name='format']").on "change", (event) =>
    console.log "Paperformat changed"
    publish_api.render()

  $("input[name='merge']").on "change", (event) =>
    console.log "Merge changed"
    publish_api.render()

  $("select[name='template']").on "change", (event) =>
    console.log "Template changed", event

    publish_api.reload
      template: event.currentTarget.value
