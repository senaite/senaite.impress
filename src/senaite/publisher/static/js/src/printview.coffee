import $ from 'jquery'
import jQuery from 'jquery'

$(document).ready ->
  console.debug '*** SENAITE.PUBLISHER.PRINTVIEW Ready'

  html = $('#reports').html()
  url = document.URL.split('printview')[0] + 'ajax_printview/process_html'

  $.ajax
    url: url
    method: 'POST'
    data:
      html: html
  .done (data) ->
      preview = $('#preview')
      preview.empty()
      preview.append data


#document.addEventListener("DOMContentLoaded", function() {
#
#  console.debug("DOM Content Loaded")
#
#  const html = document.getElementById("publisher")
#  const url = document.URL.split("printview")[0] + "ajax_printview/process_html"
#
#  fetch(url, {
#    method: "POST",
#    body: {
#      html: html
#    }
#  }).then((data) => {
#
#      debugger
#  })
#
#
#});
# */
#
#import React from 'react';
#import ReactDOM from 'react-dom';
#
#const container = document.getElementById('container');
#
#const app = (
#    <div>
#        <h1>JSX</h1>
#        <span>My first JSX span!</span>
#    </div>
#);
#ReactDOM.render(app, container); */
