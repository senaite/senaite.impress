import PublishAPI from './api.coffee'


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
