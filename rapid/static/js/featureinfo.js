class FeatureInfo {
	// auto excluded properties (feature ids)
	excludes = ['fid','ogc_fid']

	constructor (overlay) {
		if (overlay)
			this.setOverlay(overlay)
	}

	setOverlay (overlay) {
		this.overlay = overlay
	    this.props = overlay.options.propertyName
	    if (this.props) {
	    	this.props = this.props.split(',').map(p=>p.trim())
	    }
	    this.displayName = overlay.layerDefn.name
	    this.layer = overlay.options.layers
	    this.url = overlay._wmsUrl || overlay._url
	}
	    
	getFeatureInfo (evt,overlay) {
		if (overlay)
			this.setOverlay(overlay)
	    const params = this.getFeatureInfoParams(evt.latlng);
	    return $.get(this.url,params).then(response => {
	    	return this.formatFeatureInfoResponse(response)
		})
	}

	formatFeatureInfoResponse (response) {
	    const resp = xml2json.docToJSON(response)
	    let html = ''
	    let itemCount = 0
	    if (resp.tagName === 'GetFeatureInfoResponse') {
	      if (resp.children) {
	        resp.children.forEach(child => {
	          let layerName = child.attr.name
	          if (layerName == this.layer) {
	        	  // use provided display name (wmslayer's title)
	        	  layerName = this.displayName
	          }
	          if (child.children) {
	            child.children.forEach(item => {
	              if (item.tagName == 'Attribute') {
	                // Raster Info: single attribute without feature(s)
	                const value = item.attr.value
	                if (value) { // skip empty rows
	                	itemCount++
		                html += `<tr><td colspan="2">${layerName}</td><td>${value}</td></tr>`
	                }
	              } 
	              else if (item.tagName == 'Feature') {
	                // Vector Info (features)
	                const id = item.attr.id
	                if (item.children) {
	                  item.children.forEach(property => {
	                    if (property.tagName == 'Attribute') {
	                      const name = property.attr.name
	                      if (!this.excludes.includes(name)) {
		                      if (!this.props || this.props.includes(name)) {
		                        const value = property.attr.value
		                        if (value) { // skip empty rows
			                        itemCount++
			                        html += `<tr><td>${layerName}</td><td>${name}</td><td>${value}</td></tr>`
		                        }
		                      }
	                      }
	                    }
	                  })
	                }
	              }
	            })
	          }
	        })
	      }
	    }
	    return html
	  }
		
	  getFeatureInfoParams (latlng) {
		// Construct parameters object for a GetFeatureInfo request at a given point
		const lat = latlng.lat
		const lon = latlng.lng
		const params = {
		  request: 'GetFeatureInfo',
		  service: 'WMS',
		  srs: 'EPSG:4326',
		  version: '1.3.0',
		  bbox: [lat, lon, lat + 0.00001, lon + 0.00001].join(','),
		  height: 100,
		  width: 100,
		  i: 0,
		  j: 0,
		  layers: this.layer,
		  query_layers: this.layer,
		  info_format: 'text/xml'
		}
		if (this.overlay.options.propertyName) {
	    	params.propertyName = this.overlay.options.propertyName 
	    }
	    return params
	 }
}
