###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"

import Button from "./component/Button.js"
import MergeToggle from "./component/MergeToggle.js"
import OrientationSelection from "./component/OrientationSelection.js"
import PaperFormatSelection from "./component/PaperFormatSelection.js"
import Reports from "./component/Reports.js"
import Preview from "./component/Preview.js"
import PublishAPI from './api.coffee'
import TemplateSelection from "./component/TemplateSelection.js"


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

    @state =
      items: @api.get_items()
      html: ""
      preview: ""
      merge: no
      format: "A4"
      orientation: "portrait"
      template: "senaite.publisher:Default.pt"

  getRequestOptions: ->
    ###
     * Options to be sent to the server
    ###
    options =
      items: @state.items.join(",")
      html: @state.html
      merge: @state.merge
      format: @state.format
      orientation: @state.orientation
      template: @state.template
    return options

  getFormatCSSClass: ->
    ###
     * Calculates the CSS class
    ###
    return "#{@state.format} #{@state.orientation}"

  renderReports: ->
    ###
     *
    ###
    me = this

    @api.render_reports @getRequestOptions()
    .then (html) ->
      me.setState
        html: html

      # me.api.render_preview me.getRequestOptions()
      # .then (preview) ->
      #   me.setState
      #     preview: preview

  componentDidUpdate: ->
    console.debug "PublishController::componentDidUpdate"
    @api.render_barcodes()

  componentDidMount: ->
    console.debug "PublishController::componentDidMount"
    @renderReports()

  handleSubmit: (event) ->
    console.log "Form Submitted"
    event.preventDefault()

  handleChange: (event) ->
    target = event.target
    value = if target.type is "checkbox" then target.checked else target.value
    name = target.name

    console.info("PublishController::handleChange: name=#{name} value=#{value}")
    @setState
      [name]: value

  render: ->

    <div className="container">

      <div className="row">
        <div className="col-sm-12">
          <div className="jumbotron">

            <form onSubmit={this.handleSubmit}>
              <hr className="my-4"/>
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
                </div>
              </div>
            </form>

          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-sm-12">
          <Preview preview={@state.preview} id="preview" className={@getFormatCSSClass()} />
        </div>
      </div>

      <div className="row">
        <div className="col-sm-12">
          <Reports html={@state.html} id="reports" className={@getFormatCSSClass()} />
        </div>
      </div>

    </div>


document.addEventListener "DOMContentLoaded", ->
  console.debug "*** SENAITE.PUBLISHER::DOMContentLoaded"
  ReactDOM.render <PublishController />, document.getElementById "publish_controller"
