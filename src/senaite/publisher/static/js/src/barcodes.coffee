import $ from 'jquery'
import "../vendor/jquery-barcode-2.0.2.js"


$(document).ready ->
  console.debug '*** SENAITE.PUBLISHER.BARCODES Ready'

  $('.barcode').each ->
    id = $(this).attr('data-id')
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
