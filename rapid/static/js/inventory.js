class Inventory {
  constructor () {
    this.data = {}
    this.styles = {}
    this.attribute = ''
    this.layer = undefined
  }

  loadStyles (url = '/static/styles.json') {
    return $.getJSON(url).then(response => {
      this.styles = response
      return this.styles
    })
  }

  loadData (url = '/static/inventory.json') {
    return $.getJSON(url).then(response => {
      this.data = response
      return this.data
    })
  }

  getColor (value) {
    if (value !== null) {
      const attr = this.getAttribute()
      const classes = this.styles.classes[attr]
      const colors = this.styles.colors[attr]
      if (colors && classes) {
        const index = classes.findIndex(x => x > value)
        if (index < 0) {
          //  not found: take last color
          return colors[colors.length - 1]
        }
        return colors[index]
      }
    }
    return 'gray'
  }

  getStyle (feature) {
    const value = feature.properties[this.getAttribute()]
    if (value === undefined) {
      return {
        radius: 3,
        color: 'gray',
        fillColor: 'gray',
        weight: 1,
        opacity: 0.5,
        fillOpacity: 0.3
      }
    } else {
      return {
        radius: 5,
        fillColor: this.getColor(value),
        color: 'white',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
      }
    }
  }

  getFeatureInfo (feature) {
    let html = '<h5 class="text-center unibar">Inventory Data</h5><table class="table table-hover table-sm"><thead><tr><th>Attribute</th><th>Value</th></tr></thead><tbody>'
    for (const [prop, value] of Object.entries(feature.properties)) {
      html += `<tr><td>${prop}</td><td>${value || "-"}</td></tr>`
    }
    return html + '</tbody></table>'
  }

  getLegendContent () {
    const attr = this.getAttribute()
    if (attr === undefined) {
      return ''
    }
    if (this.styles === undefined) {
      return ''
    }
    const colors = this.styles.colors[attr]
    const classes = this.styles.classes[attr]
    if (classes === undefined || colors === undefined) {
      return ''
    }
    let html = `<strong>${attr}</strong>`
    for (let i = 0; i < classes.length; i++) {
      let txt = ''
      if (i === 0) {
        txt = `<  ${classes[i]}`
      } else if (i < classes.length - 1) {
        txt = `${classes[i - 1]} - ${classes[i]}`
      } else {
        txt = `> ${classes[i - 1]}`
      }
      html += `<div><i class="fas fa-circle fa-xs pr-2" style="color:${colors[i]}"></i>${txt}</div>`
    }
    html += '<div><i class="fas fa-circle fa-xs pr-2" style="color:gray"></i>no data</div>'
    return html
  }

  getAttribute () {
    return this.attribute
  }

  createLayer (data) {
    this.data = data
    const attr = this.getAttribute()
    this.layer = L.geoJSON(data, {
      onEachFeature: (feature, layer) => {
        if (attr) {
          const value = feature.properties[attr] || "no data"
          layer.bindTooltip(`${attr}: ${value}`)
        }
        layer.bindPopup(this.getFeatureInfo(feature), { maxWidth: 800 })
      },
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, this.getStyle(feature))
      }
    })
    return this.layer
  }

  redraw (map) {
    if (this.layer) {
      this.layer.remove()
      this.layer = undefined
    }
    this.createLayer(this.data).addTo(map)
  }
}
