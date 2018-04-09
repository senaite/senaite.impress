###
 * Publish API Module
###

import $ from 'jquery'
import "./lib/jquery-barcode-2.0.2.js"


class PublishAPI

  constructor: ->
    console.debug "PublishAPI::constructor"
    return @

  get_api_url: (endpoint) ->
    ###
     * Build API URL for the given endpoint
     * @param {string} endpoint
     * @returns {string}
    ###
    api_endpoint = "ajax_publish"
    segments = location.pathname.split "/"
    current_view = segments[segments.length-1]
    base_url = document.URL.split(current_view)[0]
    return "#{base_url}#{api_endpoint}/#{endpoint}"

  get_url_parameter: (name) ->
    ###
     * Parse a request parameter by name
    ###
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]')
    regex = new RegExp('[\\?&]' + name + '=([^&#]*)')
    results = regex.exec(location.search)
    if results == null then '' else decodeURIComponent(results[1].replace(/\+/g, ' '))

  get_items: ->
    ###
     * Parse the `items` request parameter and returns the UIDs in an array
    ###
    return @get_url_parameter("items").split(",")

  get_json: (endpoint, options) ->
    ###
     * Fetch Ajax API resource from the server
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
    ###
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

  fetch_reports: (data) ->
    ###
     * Fetch the generated reports HTML from the server
     * @returns {Promise}
    ###
    options =
      data: data
    return @get_json("render_reports", options)

  fetch_previews: (data) ->
    ###
     * Fetch the generated previews HTML (including PNGs) from the server
     * @returns {Promise}
    ###
    options =
      data: data
    return @get_json("load_preview", options)

  fetch_templates: ->
    ###
     * Fetch available templates
     * @returns {Promise}
    ###
    return @get_json "templates",
      method: "GET"

  fetch_paperformats: ->
    ###
     * Fetch paperformats from the server
     * @returns {Promise}
    ###
    return @get_json "paperformats",
      method: "GET"

  render_barcodes: ->
    ###
     * Render Barcodes
    ###
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

export default PublishAPI
