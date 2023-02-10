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
    @handleModalSubmit = @handleModalSubmit.bind(this)
    @loadReports = @loadReports.bind(this)
    @saveReports = @saveReports.bind(this)
    @on_row_order_change = @on_row_order_change.bind(this)

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
      reload_after_reorder: no
      reload_required: no

    window.impress = @

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
    window.addEventListener("listing:row_order_change", @on_row_order_change, false);

    @api.fetch_config().then (
      (config) ->
        @setState config, @loadReports
      ).bind(this)


  componentWillUnmount: ->
    window.removeEventListener("listing:row_order_change", @on_row_order_change, false);


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
      reload_required: no

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


  ###
    * Toggle the loader on or off
  ###
  toggleLoader: (toggle, options) ->
    options ?= {}
    state = Object.assign {loading: toggle}, options
    @setState state


  ###
    * Generate PDF and return it as a blob
  ###
  createPDF: () ->
    # Set the loader
    @toggleLoader on, loadtext: "Generating PDF ..."

    options = @getRequestOptions()
    promise = @api.create_pdf options

    promise.then =>
      # toggle the loader off
      @toggleLoader off

    return promise


  ###
    * Save all PDFs to the Server
  ###
  saveReports: (event) ->
    event.preventDefault()

    # Set the loader
    @toggleLoader on, loadtext: "Generating PDF ..."

    # generate the reports via the API asynchronously
    request_data = @getRequestOptions()
    request_data.action = event.currentTarget.name
    promise = @api.save_reports request_data

    me = this
    promise.then (redirect_url) =>
      # toggle the loader off
      @toggleLoader off
      window.location.href = redirect_url
    .catch (error) ->
      me.setState
        html: ""
        loading: no
        error: error.toString()


  ###
   * Fetch the HTML of the given URL and render it in a Modal
  ###
  loadModal: (url) ->
    el = $("#impress_modal")
    action = @getActionByURL url

    # add the UIDs of the reports as request parameters
    url = new URL(url)
    url.searchParams.append("uids", @state.items)

    # load the modal HTML with a GET request
    request = new Request(url)
    fetch(request).then (response) =>
      return response.text().then (text) =>
        el.empty()
        el.append(text)
        el.one "submit", @handleModalSubmit
        return el.modal("show")


  ###
   * Lookup action config by URL
  ###
  getActionByURL: (url) ->
    action = {}
    for item in @state.custom_actions
      if item.url == url
        action = item
        break
    return action


  ###
    * Send asynchronous HTTP POST request to the given URL
  ###
  postAction: (url, formdata) ->
    # Always generate the PDF first and attach it to the POST payload
    promise = @createPDF().then (pdf) =>
      formdata ?= new FormData()
      # Append the generated PDF for the action handler
      formdata.append("pdf", pdf)
      # Append more useful data for the action handler
      formdata.append("html", @state.html)
      formdata.append("format", @state.format)
      formdata.append("orientation", @state.orientation)
      formdata.append("template", @state.template)
      formdata.append("uids", @state.items.join(","))

      fetch url,
        method: "POST",
        body: formdata
      .then (response) =>
        @handleActionResponse response
      .catch (error) =>
        @handleActionError error


  ###
    * Handle the response data of an action provider
  ###
  handleActionResponse: (response) ->
    if not response.ok
      return @handleActionError response.statusText
    response.blob().then (blob) =>
      # NOTE: type is different per browser, e.g.:
      #       -> FireFox: "text/html; charset=utf-8"
      #       -> Chrome:  "text/html"
      type = blob.type
      # handle PDF responses
      if type.startsWith("application/pdf")
        return @handleActionBlobResponse blob
      # handle all other types as text
      return blob.text().then (text) =>
        if type.startsWith("application/json")
          # XXX currently not handled any further
          return @handleActionJSONResponse JSON.parse(text)
        if type.startsWith("text/html")
          return @handleActionHTMLResponse text


  ###
    * Open blob in new window
  ###
  handleActionBlobResponse: (blob) ->
    url= window.URL.createObjectURL(blob)
    window.open(url, "_blank")


  ###
    * Reload the HTML into the modal to support statusmessages
  ###
  handleActionHTMLResponse: (html) ->
    modal = $("#impress_modal")
    modal.empty()
    modal.append(html)
    modal.one "submit", @handleModalSubmit
    modal.modal("show")


  handleActionJSONResponse: (json) ->
    console.warn "Action returned JSON object, which is currently not handled! => ", json


  handleActionError: (error) ->
    console.error error


  ###
    * Event handler when the form inside the Modal was submitted
  ###
  handleModalSubmit: (event) ->
    event.preventDefault()

    # use event.target to get the form instead of the modal
    form = event.target
    modal = event.currentTarget
    url = form.action
    action = @getActionByURL(url)
    formdata = new FormData(form)

    # check if the modal should stay open or be closed
    if action.close_after_submit is not false
      modal.modal("hide")

    # post the action
    @postAction url, formdata


  handleSubmit: (event) ->
    event.preventDefault()


  ###
    * Event handler when one of the report controls changed
    *
    * This will regenerate the PDF previews
  ###
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

    url = target.getAttribute("url")
    action = @getActionByURL(url)

    if action.modal isnt false
      # load the action modal
      return @loadModal url
    # post data directly to the action URL
    return @postAction url


  ###
    * Event handler when the object order was changed in the listing table
    *
    * @param {CustomEvent} event: provides the current `folderitems` of the listing
  ###
  on_row_order_change: (event) ->
    uids = event.detail.folderitems.map (item) => item.uid

    if @state.reload_after_reorder
      @setState items: uids, @loadReports
    else
      @setState items: uids, reload_required: yes


  render: ->
    <div className="col-sm-12">
      <Modal className="modal fade" id="impress_modal" />
      {@state.reload_required and
      <div className="alert alert-warning">
        <h4 className="alert-heading">
        <span className="mr-2">Reload is required</span>
        <Button name="reload" title="↺" onClick={@loadReports} className="btn btn-sm btn-outline-success" />
        </h4>
      </div>}
      <form name="publishform" onSubmit={this.handleSubmit}>
        <div className="form-group">
          <div className="input-group">
            <TemplateSelection api={@api} onChange={@handleChange} value={@state.template} className="custom-select" name="template" />
            <PaperFormatSelection api={@api} onChange={@handleChange} value={@state.format} className="custom-select" name="format" />
            <OrientationSelection api={@api} onChange={@handleChange} value={@state.orientation} className="custom-select" name="orientation" />
            <div className="input-group-append">
              <Button name="reload" title="↺" onClick={@loadReports} className="btn btn-outline-success"/>
              {@state.custom_actions.map((action, index) => <Button onClick={@handleCustomAction} key={action.name | index} title={action.title} text={action.text} name={action.name} className={action.css_class || "btn btn-outline-secondary"} {...action} />)}
              {@state.allow_email and <Button name="email" title="Email" onClick={@saveReports} className="btn btn-outline-secondary" />}
              {@state.allow_save and <Button name="save" title="Save" onClick={@saveReports} className="btn btn-outline-secondary" />}
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
