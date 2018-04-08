###
 * Publish API Module
###

import $ from 'jquery'
import "./lib/jquery-barcode-2.0.2.js"


class PublishAPI

  constructor: ->
    console.debug "PublishAPI::constructor"
    return @

  get_api_url: (endpoint) =>
    ###
     * Get the Publish API URL
    ###
    api_endpoint = "ajax_publish"
    segments = location.pathname.split "/"
    current_view = segments[segments.length-1]
    base_url = document.URL.split(current_view)[0]
    return "#{base_url}#{api_endpoint}/#{endpoint}"

  get_url_parameter: (name) ->
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]')
    regex = new RegExp('[\\?&]' + name + '=([^&#]*)')
    results = regex.exec(location.search)
    if results == null then '' else decodeURIComponent(results[1].replace(/\+/g, ' '))

  get_json: (endpoint, options) =>
    options ?= {}

    method = options.method or "POST"
    data = JSON.stringify(options.data) or "{}"

    url = @get_api_url endpoint
    init =
      method: method
      headers:
        "Content-Type": "application/json"
      body: if method is "POST" then data else null
      credentials: "include"
    console.info "PublishAPI::fetch:endpoint=#{endpoint} init=",init
    request = new Request(url, init)
    return fetch(request).then (response) ->
      return response.json()

  render_reports: (data) =>
    ###
     * Render Reports HTML
    ###
    options =
      data: data
    return @get_json("render_reports", options).then (response) ->
      el = document.getElementById("preview")
      el.innerHTML = response

  fetch_paperformats: =>
    ###
     * Fetch available paperformats
    ###
    return @get_json "paperformats",
      method: "GET"

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


export default PublishAPI
