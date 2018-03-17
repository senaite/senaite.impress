import $ from 'jquery';

$(document).ready(function () {
  console.debug("Document Ready")
  var html = $("#publisher").html()
  $.ajax({
    url: "/bikalims/analysisrequests/ajax_printview/process_html",
    method: "POST",
    data: {
      html: html
    }
  }).done(function(data){
    $("#publisher").html(data)
  })
})

// import React from 'react';
// import ReactDOM from 'react-dom';

// const container = document.getElementById('container');

// const app = (
//     <div>
//         <h1>JSX</h1>
//         <span>My first JSX span!</span>
//     </div>
// );
// ReactDOM.render(app, container);
