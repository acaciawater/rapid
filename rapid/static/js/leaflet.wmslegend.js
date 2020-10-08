/*
 * L.Control.WMSLegend is used to add a WMS Legend to the map
 */

L.Control.WMSLegend = L.Control.extend({
  options: {
    position: 'topright',
    uri: '',
    title: ''
  },

  onAdd: function () {
    var controlClassName = 'leaflet-control-wms-legend'
    var legendClassName = 'wms-legend'
    var stop = L.DomEvent.stopPropagation
    this.container = L.DomUtil.create('div', controlClassName)
    this.container.innerHTML += '<p><strong>' + this.options.title + '</strong></p>'
    this.img = L.DomUtil.create('img', legendClassName, this.container)
    this.img.src = this.options.uri
    this.img.alt = 'Legend'

    L.DomEvent
      .on(this.img, 'click', this._click, this)
      .on(this.container, 'click', this._click, this)
      .on(this.img, 'mousedown', stop)
      .on(this.img, 'dblclick', stop)
      .on(this.img, 'click', L.DomEvent.preventDefault)
      .on(this.img, 'click', stop)
    this.height = null
    this.width = null
    return this.container
  },
  _click: function (e) {
    L.DomEvent.stopPropagation(e)
    L.DomEvent.preventDefault(e)
    // toggle legend visibility
    var style = window.getComputedStyle(this.img)
    if (style.display === 'none') {
      this.container.style.height = this.height + 'px'
      this.container.style.width = this.width + 'px'
      this.img.style.display = this.displayStyle
    } else {
      if (this.width === null && this.height === null) {
        // Only do inside the above check to prevent the container
        // growing on successive uses
        this.height = this.container.offsetHeight
        this.width = this.container.offsetWidth
      }
      this.displayStyle = this.img.style.display
      this.img.style.display = 'none'
      this.container.style.height = '20px'
      this.container.style.width = '20px'
    }
  }
})

L.wmsLegend = function (options) {
  var wmsLegendControl = new L.Control.WMSLegend
  wmsLegendControl.options = options
  return wmsLegendControl
}
