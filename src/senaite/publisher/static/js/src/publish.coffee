###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"

import PublishAPI from './api.coffee'

import Button from "./components/Button.js"
import Loader from "./components/Loader.js"
import MergeToggle from "./components/MergeToggle.js"
import OrientationSelection from "./components/OrientationSelection.js"
import PaperFormatSelection from "./components/PaperFormatSelection.js"
import Preview from "./components/Preview.js"
import ReportHTML from "./components/ReportHTML.js"
import TemplateSelection from "./components/TemplateSelection.js"


# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** SENAITE.PUBLISHER::DOMContentLoaded"
  controller = ReactDOM.render <PublishController />, document.getElementById "publish_controller"

  # Bind the event listener on the download buttons
  buttons = document.querySelectorAll ".download-pdf-button"
  buttons.forEach (button) ->
    button.addEventListener "click", controller.downloadPDF


class PublishController extends React.Component
  ###
   * Publish Controller
  ###

  constructor: (props) ->
    super(props)
    console.log "PublishController::constructor:props=", props

    @api = new PublishAPI()
    @T = window.jarn.i18n.MessageFactory("senaite.publisher")

    # Bind `this` in methods
    @handleSubmit = @handleSubmit.bind(this)
    @handleChange = @handleChange.bind(this)
    @loadReports = @loadReports.bind(this)
    @downloadPDF = @downloadPDF.bind(this)

    @state =
      items: @api.get_items()
      html: ""
      preview: ""
      merge: no
      format: "A4"
      orientation: "portrait"
      template: "senaite.publisher:MultiDefault.pt"
      loading: yes
      loadtext: ""
      group_by_client: yes


  getRequestOptions: ->
    ###
     * Options to be sent to the server
    ###
    options =
      items: @state.items
      html: @getProcessedReportHTML()
      merge: @state.merge
      format: @state.format
      orientation: @state.orientation
      template: @state.template
      group_by_client: @state.group_by_client

    console.debug("Request Options=", options)
    return options


  getProcessedReportHTML: ->
    ###
     * Extracts the HTML from the `<div id="reports"/>` element
     * N.B. This step is necessary, so that JS can modify the DOM before
     *      generating the Preview/PDF from it
    ###

    # ensure that the rendered HTML has the right format/orientation CSS classes
    @setCSS()
    el = document.getElementById "reports"
    return "" unless el
    return el.innerHTML


  loadReports: ->
    ###
     * Load Reports and generate a PNG preview
     *
     * 1. Fetch report HTML for the UIDs from the server
     * 2. Set the HTML in the state which renders the reports into the DOM (invisible)
     * 3. Client local JS, e.g. Barcode, Graphs etc. modify the loaded HTML
     * 4. Send the updated HTML back to the Server for preview generation
     * 5. Render Preview HTML into the DOM
    ###

    # Set the loader
    @setState
      html: ""
      preview: ""
      loading: yes
      loadtext: @T("Loading Reports...")

    # fetch the rendered reports via the API asynchronously
    promise = @api.render_reports @getRequestOptions()

    promise.then ((html) ->
      @setState
        html: html
      # load the preview
      @loadPreview()
    ).bind(this)


  loadPreview: ->
    ###
     * Send the processed HTML to the server to generate a preview
    ###

    # Set the loader
    @setState
      loading: yes
      preview: ""
      loadtext: @T("Loading Preview...")

    # fetch the rendered previews via the API asynchronously
    promise = @api.load_preview @getRequestOptions()

    promise.then ((preview) ->
      @setState
        preview: preview
        loading: no
    ).bind(this)


  setCSS: ->
    ###
     * Set the CSS Classes according to the paper format
    ###
    cls = "#{@state.format} #{@state.orientation}"

    # set the CSS Class on the <body>
    body = document.querySelector "body"
    body.className = cls

    # set the CSS Class on all reports
    reports = document.querySelectorAll ".report"
    reports.forEach (report) ->
      report.className = "report #{cls}"


  componentDidUpdate: ->
    console.debug "PublishController::componentDidUpdate"

    # render the barcodes
    @api.render_barcodes()

    # update the CSS of all rendered elements
    @setCSS()

    # Toggle PDF download buttons
    if @isMultiReport()
      @toggleDownloadButtons yes
    else
      @toggleDownloadButtons no


  toggleDownloadButtons: (toggle) ->
    buttons = document.querySelectorAll ".download-pdf-button"
    buttons.forEach (button) ->
        button.disabled = toggle


  componentDidMount: ->
    console.debug "PublishController::componentDidMount"
    @loadReports()


  handleSubmit: (event) ->
    event.preventDefault()


  downloadPDF: (event) ->
    event.preventDefault()

    # Set the loader
    @setState
      loading: yes
      loadtext: "Loading PDF..."

    options = @getRequestOptions()

    target = event.target

    uid = target.getAttribute "uid"
    if uid
      options.uid = uid

    name = target.getAttribute "name"
    if name
      options.name = name

    promise = @api.download_pdf options

    promise.then ( ->
      @setState
        loading: no
    ).bind(this)


  handleChange: (event) ->
    target = event.target
    value = if target.type is "checkbox" then target.checked else target.value
    name = target.name

    console.info("PublishController::handleChange: name=#{name} value=#{value}")
    @setState
      [name]: value
    , ->
      if name == "template"
        # reload HTML and Preview if the template changed
        return @loadReports()
      # reload only the Preview
      return @loadPreview()


  isMultiReport: ->
    return @state.template.search("Multi") > -1


  render: ->
    <div className="col-sm-12">
      <form name="publishform" onSubmit={this.handleSubmit}>
        <div className="form-group">
          <div className="input-group">
            <div className="input-group-prepend">
              <div className="input-group-text">
                <MergeToggle api={@api} onChange={@handleChange} value={@state.merge} className="" name="merge" />
              </div>
            </div>
            <TemplateSelection api={@api} onChange={@handleChange} value={@state.template} className="custom-select" name="template" />
            <PaperFormatSelection api={@api} onChange={@handleChange} value={@state.format} className="custom-select" name="format" />
            <OrientationSelection api={@api} onChange={@handleChange} value={@state.orientation} className="custom-select" name="orientation" />
            <div className="input-group-append">
              <Button onClick={@loadReports} name="reload" title="↺" className="btn btn-outline-success"/>
              <Button title="PDF" onClick={@downloadPDF} className="btn btn-outline-secondary" />
            </div>
          </div>
        </div>
      </form>
      <hr className="my-2"/>
      <div className="row">
        <div className="col-sm-12">
          <Loader loadtext={@state.loadtext} loading={@state.loading} />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-12">
          <Preview preview={@state.preview} id="preview" className="row" />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-12">
          <ReportHTML html={@state.html} id="reports" className="d-none" />
        </div>
      </div>
    </div>
