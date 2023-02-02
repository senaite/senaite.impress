###
 * Publish API Module
###

import $ from 'jquery'
import "./lib/jquery-barcode-2.0.2.js"


class PublishAPI

  constructor: ->
    console.debug "PublishAPI::constructor"
    return @


  parse_html: (html) ->
    ###
     * Parse the HTML to a DOM element
    ###
    parser = new DOMParser()
    return parser.parseFromString(html, "text/html")


  get_base_url: ->
    ###
     * Calculate the current base url
    ###
    return document.URL.split("?")[0]


  get_api_url: (endpoint) ->
    ###
     * Build API URL for the given endpoint
     * @param {string} endpoint
     * @returns {string}
    ###
    api_endpoint = "ajax_publish"
    segments = location.pathname.split "/"
    current_view = segments[segments.length-1]
    url = @get_base_url().split(current_view)[0]
    # we also pass back eventual query parameters to the API
    params = location.search
    return "#{url}#{api_endpoint}/#{endpoint}#{params}"


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
    items = @get_url_parameter("items")
    return items.split(",")


  get_reports: (uids) ->
    ###
     * Fetch the JSON data of all the reports
    ###
    if not uids
      uids = @get_items()
    options =
      data:
        items: uids
    return @get_json("get_reports", options)


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
        "X-CSRF-TOKEN": @get_csrf_token()
      body: if method is "POST" then data else null
      credentials: "include"
    console.info "PublishAPI::fetch:endpoint=#{endpoint} init=",init
    request = new Request(url, init)
    return fetch(request).then (response) ->
      if response.status isnt 200
        return response.json().then (json) ->
          throw new Error(json.error or "Unknown Error")
      else
        return response.json()


  render_reports: (data) ->
    ###
     * Fetch the generated reports HTML from the server
     * @returns {Promise}
    ###
    options =
      data: data
    return @get_json("render_reports", options)


  save_reports: (data) ->
    ###
     * @returns {Promise}
    ###

    options =
      data: data
    return @get_json("save_reports", options)


  create_pdf: (options) ->
    # wrap all options into form data
    formData = new FormData()
    formData.set("download", "1")
    for key, value of options
      formData.set(key, value)

    # Prepare the POST request
    url = @get_base_url()
    init =
      method: "POST"
      body: formData
      credentials: "include"
    request = new Request(url, init)

    # submit the POST and display the PDF in a new window
    return fetch(request).then (response) ->
      return response.blob()


  print_pdf: (options) ->
    ###
     * Send an async request to the server and download the file
    ###

    @create_pdf(options).then (blob) ->
      # open the PDF in a separate window
      url= window.URL.createObjectURL(blob)
      window.open(url, "_blank")

      # Alternate way to download a named PDF
      #
      # window.URL.revokeObjectURL(url)
      # use this for immediate download
      # fileLink = document.createElement("a")
      # fileLink.href = url
      # fileLink.download = options.filename or "Report.pdf"
      # fileLink.click()


  load_preview: (data) ->
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


  fetch_config: ->
    ###
     * Fetch default config
     * @returns {Promise}
    ###
    return @get_json "config",
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

  render_ranges: ->
    ###
     * Render ranges (graphs)
    ###
    new RangeGraph().load()
    @convert_svg_to_image()

  convert_svg_to_image: ->
    ###
     * Convert SVGs to Images
    ###
    jQuery("svg").each ->
      console.debug "Convert SVG to IMG: ", @
      img = document.createElement "img"
      img.src = "data:image/svg+xml;base64," + btoa($(@).parent().html())
      jQuery(@).replaceWith(img)


  get_csrf_token: () ->
    ###
     * Get the plone.protect CSRF token
     * Note: The fields won't save w/o that token set
    ###
    return document.querySelector("#protect-script").dataset.token


export default PublishAPI
