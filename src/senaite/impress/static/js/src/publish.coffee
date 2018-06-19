###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"

import PublishAPI from './api.coffee'

import Button from "./components/Button.js"
import ErrorBox from "./components/ErrorBox.js"
import Loader from "./components/Loader.js"
import MergeToggle from "./components/MergeToggle.js"
import OrientationSelection from "./components/OrientationSelection.js"
import PaperFormatSelection from "./components/PaperFormatSelection.js"
import Preview from "./components/Preview.js"
import ReportHTML from "./components/ReportHTML.js"
import TemplateSelection from "./components/TemplateSelection.js"


# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** SENAITE.IMPRESS::DOMContentLoaded: --> Loading ReactJS Controller"
  # gather the <div> container from publish.pt and load the component
  controller = ReactDOM.render <PublishController />, document.getElementById "publish_controller"


class PublishController extends React.Component
  ###
   * Publish Controller
  ###

  constructor: (props) ->
    super(props)
    console.log "PublishController::constructor:props=", props

    @api = new PublishAPI()

    # Bind `this` in methods
    @handleSubmit = @handleSubmit.bind(this)
    @handleChange = @handleChange.bind(this)
    @loadReports = @loadReports.bind(this)
    @saveReports = @saveReports.bind(this)

    @state =
      items: @api.get_items()
      html: ""
      preview: ""
      merge: no
      format: "A4"
      orientation: "portrait"
      template: ""
      loading: no
      loadtext: ""
      error: ""


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

    console.debug("Request Options=", options)
    return options


  getProcessedReportHTML: ->
    ###
     * Extracts the HTML from the `<div id="reports"/>` element
     * N.B. This step is necessary, so that JS can modify the DOM before
     *      generating the Preview/PDF from it
    ###

    # ensure that the rendered HTML has the right format/orientation CSS classes
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
      error: ""
      loading: yes
      loadtext: "Loading Reports..."

    # fetch the rendered reports via the API asynchronously
    promise = @api.render_reports @getRequestOptions()

    me = this
    promise.then (html) ->
      me.setState
        html: html
      me.loadPreview()
    .catch (error) ->
      me.setState
        html: ""
        loading: no
        error: error.toString()

  loadPreview: ->
    ###
     * Send the processed HTML to the server to generate a preview
    ###

    # Set the loader
    @setState
      loading: yes
      preview: ""
      loadtext: "Loading Preview..."

    # fetch the rendered previews via the API asynchronously
    promise = @api.load_preview @getRequestOptions()

    promise.then ((preview) ->
      @setState
        preview: preview
        loading: no
    ).bind(this)


  saveReports: (event) ->
    ###
     * Save all PDFs to the Server
    ###
    event.preventDefault()

    # Set the loader
    @setState
      loading: yes
      loadtext: "Generating PDFs..."

    # generate the reports via the API asynchronously
    request_data = @getRequestOptions()
    request_data.action = event.currentTarget.name
    promise = @api.save_reports request_data

    promise.then ((redirect_url) ->
      # toggle the loader off
      @setState
        loading: no
      window.location.href = redirect_url
    ).bind(this)


  componentDidUpdate: ->
    ###
     * ReactJS event handler when the component did update
     *
     * That looks like the right place to process the "raw" HTML from the server
     * with JavaScript, like barcode rendering etc.
    ###
    console.debug "PublishController::componentDidUpdate"

    # render the barcodes
    @api.render_barcodes()


  componentDidMount: ->
    console.debug "PublishController::componentDidMount"

    @api.fetch_config().then (
      (config) ->
        @setState config, @loadReports
      ).bind(this)


  handleSubmit: (event) ->
    event.preventDefault()


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
    ###
     * Publication UI
    ###
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
              <Button name="reload" title="↺" onClick={@loadReports} className="btn btn-outline-success"/>
              <Button name="email" title="Email" onClick={@saveReports} className="btn btn-outline-secondary" />
              <Button name="save" title="Save" onClick={@saveReports} className="btn btn-outline-secondary" />
            </div>
          </div>
        </div>
      </form>
      <hr className="my-2"/>
      <div className="row">
        <div className="col-sm-12">
          <Loader loadtext={@state.loadtext} loading={@state.loading} />
        </div>
        <div className="col-sm-12">
          <ErrorBox error={@state.error}  />
        </div>
      </div>
      <Preview preview={@state.preview} id="preview" className="row" />
      <ReportHTML html={@state.html} id="reports" className="d-none" />
    </div>
