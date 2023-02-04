###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"

import PublishAPI from "./api.coffee"

import Button from "./components/Button.js"
import ErrorBox from "./components/ErrorBox.js"
import Loader from "./components/Loader.js"
import OrientationSelection from "./components/OrientationSelection.js"
import PaperFormatSelection from "./components/PaperFormatSelection.js"
import Preview from "./components/Preview.js"
import ReportHTML from "./components/ReportHTML.js"
import ReportOptions from "./components/ReportOptions.js"
import TemplateSelection from "./components/TemplateSelection.js"
import Modal from "./components/Modal.js"


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
    @handleCustomAction = @handleCustomAction.bind(this)
    @loadReports = @loadReports.bind(this)
    @saveReports = @saveReports.bind(this)
    @printReports = @printReports.bind(this)

    @state =
      items: @api.get_items()
      html: ""
      preview: ""
      format: "A4"
      orientation: "portrait"
      template: ""
      loading: no
      loadtext: ""
      error: ""
      controls: ""
      report_options: {}
      allow_save: yes
      allow_email: yes
      custom_actions: []


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

    # render range graphs
    @api.render_ranges()


  componentDidMount: ->
    console.debug "PublishController::componentDidMount"

    @api.fetch_config().then (
      (config) ->
        @setState config, @loadReports
      ).bind(this)


  getRequestOptions: ->
    ###
     * Options to be sent to the server
    ###
    options =
      items: @state.items
      html: @getProcessedReportHTML()
      format: @state.format
      orientation: @state.orientation
      template: @state.template
      report_options: @state.report_options

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

      # parse the html into a DOM element
      doc = me.api.parse_html html

      # parse the report controls div
      controls = doc.getElementById "controls"
      if controls isnt null
        me.setState
          controls: controls.innerHTML
      else
        me.setState
          controls: ""

      me.setState
        html: html
      , ->
        # At this point we can be sure that the HTML is in the DOM
        console.debug "Report HTML in DOM, loading scripts & preview"
        me.loadScripts()
        me.loadPreview()
    .catch (error) ->
      me.setState
        html: ""
        loading: no
        error: error.toString()


  loadScripts: ->
    ###
     * Execute inline JavaScripts
    ###
    me = this

    reports = document.getElementsByClassName "report"
    $.each reports, (index, report) ->
      scripts = report.getElementsByTagName "script"
      $.each scripts, (index, script) ->
        try
          text = script.innerText
          window.eval text
        catch error
          me.setState
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

    me = this
    promise.then (preview) ->
      me.setState
        preview: preview
        loading: no
    .catch (error) ->
      me.setState
        html: ""
        loading: no
        error: error.toString()


  toggleLoader: (toggle, options) ->
    options ?= {}
    state = Object.assign {loading: toggle}, options
    @setState state


  createPDF: () ->
    # Set the loader
    @toggleLoader yes, loadtext: "Generating PDF ..."

    options = @getRequestOptions()
    promise = @api.create_pdf options

    promise.then =>
      # toggle the loader off
      @toggleLoader off

    return promise


  printReports: (event) ->
    ###
     * Print all PDFs
    ###
    event.preventDefault()

    target = event.currentTarget

    # Set the loader
    @setState
      loading: yes
      loadtext: "Generating PDF..."

    options = @getRequestOptions()

    # print the PDF
    promise = @api.print_pdf options

    me = this
    promise.then ->
      # toggle the loader off
      me.setState
        loading: no
    .catch (error) ->
      me.setState
        loading: no
        error: error.toString()


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

    me = this
    promise.then (redirect_url) ->
      # toggle the loader off
      me.setState
        loading: no
      window.location.href = redirect_url
    .catch (error) ->
      me.setState
        html: ""
        loading: no
        error: error.toString()


  loadModal: (url, pdf, action) ->
    el = $("#impress_modal")
    action ?= {}

    url = new URL(url)
    url.searchParams.append("uids", @state.items)

    # submit callback
    on_submit = (event) =>
      event.preventDefault()

      if action.close_after_submit is not false
        el.modal("hide")

      # prepare formdata of the modal form
      form = event.currentTarget
      formdata = new FormData(form)

      if not form.action
        console.error "Modal form has no action defined"
        return

      # post the action
      @postAction form.action, pdf, formdata

    request = new Request(url)
    fetch(request)
    .then (response) ->
      return response.text().then (text) ->
        el.empty()
        el.append(text)
        el.one "submit", on_submit
        return el.modal("show")

  ###
   * Lookup action config by name
  ###
  getActionByName: (name) ->
    action = {}
    for item in @state.custom_actions
      if item.name == name
        action = item
        break
    return action


  ###
    * Send asynchronous HTTP POST request to the given URL
  ###
  postAction: (url, pdf, formdata) ->
    formdata ?= new FormData()
    # Append the generated PDF for the action handler
    formdata.append("pdf", pdf)
    # Append more useful data for the action handler
    formdata.append("html", @state.html)
    formdata.append("format", @state.format)
    formdata.append("orientation", @state.orientation)
    formdata.append("template", @state.template)
    formdata.append("uids", @state.items.join(","))

    # process the modal form submit
    fetch url,
      method: "POST",
      body: formdata
    .then (response) =>
      if not response.ok
        return Promise.reject(response)
      return response.blob().then (blob) =>
        if not blob.type.startsWith("text")
          url = window.URL.createObjectURL(blob)
          return window.open(url, "_blank")
        return blob.text().then (text) =>
          # allow redirects when the modal form returns an URL
          if text.startsWith("http")
            window.location = text
          return
    .catch (error) =>
      console.error(error)


  handleSubmit: (event) ->
    event.preventDefault()


  handleChange: (event) ->
    target = event.currentTarget
    value = if target.type is "checkbox" then target.checked else target.value
    name = target.name
    option =
      [name]: value
    console.info "PublishController::handleChange: name=#{name} value=#{value}"

    if name not in @state
      # Put unknown keys into the report_options object.
      # These keys will be passed directly to the report in the `options` mapping
      option = @state.report_options
      option[name] = value

    # Reload the whole report
    @setState option, @loadReports


  ###
    * Event handler for custom action providers
    *
    * Custom action providers are loaded when the config is fetched in componentDidMount
  ###
  handleCustomAction: (event) ->
    event.preventDefault()
    target = event.currentTarget

    name = target.getAttribute("name")
    action = @getActionByName(name)

    if not action
      console.error "No action found for #{name}"
      return

    # get the URL from the action
    url = action.url

    if not url
      console.error "Custom action has no URL defined!"
      return

    # Always create the PDF
    promise = @createPDF()

    promise.then (pdf) =>
      if action.modal isnt false
        # load the action modal
        return @loadModal url, pdf, action
      # post data directly to the action URL
      return @postAction url, pdf


  render: ->
    <div className="col-sm-12">
      <Modal className="modal fade" id="impress_modal" />
      <form name="publishform" onSubmit={this.handleSubmit}>
        <div className="form-group">
          <div className="input-group">
            <TemplateSelection api={@api} onChange={@handleChange} value={@state.template} className="custom-select" name="template" />
            <PaperFormatSelection api={@api} onChange={@handleChange} value={@state.format} className="custom-select" name="format" />
            <OrientationSelection api={@api} onChange={@handleChange} value={@state.orientation} className="custom-select" name="orientation" />
            <div className="input-group-append">
              <Button name="reload" title="↺" onClick={@loadReports} className="btn btn-outline-success"/>
              {@state.allow_email and <Button name="email" title="Email" onClick={@saveReports} className="btn btn-outline-secondary" />}
              {@state.allow_save and <Button name="save" title="Save" onClick={@saveReports} className="btn btn-outline-secondary" />}
              {@state.custom_actions.map((action, index) => <Button onClick={@handleCustomAction} key={action.name | index} title={action.title} text={action.text} name={action.name} className={action.css_class || "btn btn-outline-secondary"} />)}
            </div>
          </div>
        </div>
      </form>
      <ReportOptions api={@api} onChange={@handleChange} controls={@state.controls} className="" name="reportcontrols" />
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
