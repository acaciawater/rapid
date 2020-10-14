/**
 * @author: theo
 */

var baseMaps = {}

var storage = sessionStorage // or localStorage?

function changeBaseLayer (e) {
  storage.setItem('baselayer', e.name)
}

function restoreMap (map) {
  let succes = false
  var name = storage.getItem('baselayer')
  if (name) {
	let bm = baseMaps[name] 
    if (bm) {
    	bm.addTo(map)
        succes = true
    }
  }
  return succes
}

function saveBounds (map) {
  const b = map.getBounds()
  const key = `bounds${map.id}`
  storage.setItem(key, b.toBBoxString())
}

function restoreBounds (map) {
  const key = `bounds${map.id}`
  const b = storage.getItem(key)
  if (b) {
    const corners = b.split(',').map(Number)
    map.fitBounds([[corners[1], corners[0]], [corners[3], corners[2]]])
    return true
  }
  return false
}

var theMap = null
var overlayLayers = []
const iconVisible = 'far fa-check-square'
const iconInvisible = 'far fa-square'
const spinner = 'fas fa-spinner fa-spin'
const warning = 'fas fa-exclamation'

function reorderOverlays (overlays) {
  // show layers in proper order on map
  overlays.forEach(overlay => {
    if (overlay.layerDefn.visible) {
      overlay.bringToFront()
    }
  })
}

function sortOverlays(overlays, order) {
	const ordered = order.map(id => overlays.find(o => o.layerDefn.id == id))
	reorderOverlays(ordered)
	return ordered
}

function toggleLayer (event, id) {
  const icon = event.target
  const overlay = overlayLayers.find(o => o.layerDefn.id === id)
  const layer = overlay.layerDefn
  const parent = $(icon).parent()
  if (theMap.hasLayer(overlay)) {
    theMap.removeLayer(overlay)
    layer.visible = false
    icon.className = icon.className.replace(iconVisible, iconInvisible)
    parent.find('.collapse').collapse('hide')
    // remove spinner if layer toggled before finished loading
	parent.find('.fa-spin').removeClass(spinner)

  } else {
    theMap.addLayer(overlay)
    layer.visible = true
    icon.className = icon.className.replace(iconInvisible, iconVisible)
    parent.find('.collapse').collapse('show')
  }
  // inform backend about visibility change
  $.post(`toggle/${id}`)
}

async function createOverlay (layer) {
	if (layer.options.service == 'WMS') {
		return layer.options.tiled? L.tileLayer.wms(layer.url, layer.options): L.nonTiledLayer.wms(layer.url, layer.options)
	} 
	else if (layer.options.service == 'WFS') {
		const wfs = new WFSLayer(layer.name)
		wfs.layer.on('add', function() {
			if (!wfs.features || wfs.features.length == 0) {
				// lazy load features
				wfs.loadFeatures(layer.url, {
					service: layer.options.service,
				    version: layer.options.version,
				  	request: 'GetFeature',
				  	typename: layer.options.layers,
				  	outputformat: 'GeoJSON'
				})
				.then(() => {
					// show the result
					wfs.redraw()
				})
			}
		})
		return wfs.layer
	} 
}

/**
 * property of a wfs layer has changed
 */
function propertyChanged(select, id) {
	const name = select.options[select.selectedIndex].value
	console.debug(id, name)
	const overlay = overlayLayers[id]
	const wfs = overlay.wfs
	overlay.fire('loading')
	wfs.filter(name).then(() => overlay.fire('load'))
	const content = wfs.getLegendContent(name)
	$(`#legend_${id} .legend-content`).html(content)
}

function opacityChanged(value, id) {
	const overlay = overlayLayers[id]
	overlay.layerDefn.options.opacity = value
	overlay.setOpacity(value)
}

function showInfo(title, url) {
  console.debug(`Info requested for ${title}`)
  return fetch(url).then(response => {
	  return response.text().then(text => {
		  $("#infoModal .modal-title").html(title)
		  $("#infoModal .modal-body").html(text)
		  $("#infoModal").modal("show")
	  })
  })
}

async function addOverlays (map, list, layers) {
  return layers.forEach(layer => {
    createOverlay(layer).then(overlay => {
	    if (overlay) {
	        const id = overlayLayers.push(overlay) - 1
		    overlay.id = id
		    overlay.layerDefn = layer
	    	const icon = layer.visible ? iconVisible : iconInvisible
		    let item = `<li id=layer_${layer.id} class="layer list-group-item py-1">
		        <i class="pr-2 pl-0 pt-1 ${icon} float-left" onclick="toggleLayer(event, ${layer.id})"></i>
		        <span data-toggle="collapse" href="#legend_${id}">${layer.name}</span>
		        <i id="status_${id}" class="float-right"></i>`
		    	
		  	if (layer.downloadable) {
		        // add download link that shows itself on hover
		    	item += `<a class="download-link" href="/ows/download/${layer.layer_id}">
		    		<i class="my-1 ml-1 fas fa-arrow-alt-circle-down float-right" title="download ${layer.name}"></i>
		    		</a>`
		    }

	        if (layer.info) {
		        // add info link that shows itself on hover
		    	item += `<a class="download-link text-primary" href="" onclick="showInfo('${layer.name}', '${layer.info}'); return false;">
		    		<i class="my-1 fas fa-info float-right" title="More on ${layer.name}"></i>
		    		</a>`
		    }

	        if (overlay.wfs) {
				overlay.wfs.loadLegend(`/ows/legends/${layer.layer_id}`).then(legends => {
		    		let select = `<select id="property_${id}" class="custom-select" onchange="propertyChanged(this,${id})"><option selected value="">Choose...</option>`
			 			let index = 1
			 			legends.filter(l => l.entries.length > 0).forEach(legend => {
			 				select += `<option value="${legend.property}">${legend.title}</option>`
			 				index++;
			 			})
			 			select += '</select>'
				    	$(`#layer_${layer.id}`).append(`<div class="collapse" id="legend_${id}">${select}<div class="legend legend-content"><div>`)
				})
	    	}
	        else {
		        // add collapsible panel for legend
		    	item += `<div class="collapse" id="legend_${id}" onclick="$(this).collapse('hide')">`
	
		    	// add opacity slider
	    		item += `<input id="opacity_${id}" type="range" min="0" max="100" value="${layer.options.opacity*100}"
		    		class="slider" title="Opacity" 
		    		onclick="event.stopPropagation()" // do not collapse when slider clicked 
		    		oninput="opacityChanged(this.value/100.0, ${id})">`
	    			
		        if (layer.legend) {
		        	// add legend graphic
			    	item += `<img class="wms-legend" src="${layer.legend}"></img>`
			    }
	        }
	        item += `</div></li>`

		    list.append(item)
		
		    const status = $(`#status_${id}`)
		    overlay.on('loading',function(evt) {
			  status.removeClass(warning)
	    	  status.attr('title', 'Loading')
		      status.addClass(spinner)
		    })
		    overlay.on('load',function(evt) {
		      status.removeClass(spinner)
		      status.removeClass(warning)
	    	  status.removeAttr('title')
		    })
		    overlay.on('error',function(evt) {
		      status.removeClass(spinner)
		      status.addClass(warning)
		      if (evt.errors) {
		    	  const msg = evt.errors.map(e => e.message).join(',')
			      status.attr('title', msg)
		      }
		      else if (evt.message) {
			      status.attr('title', evt.message)
		      }
		      else {
		    	  status.removeAttr('title')
		      }
		    })
		    if (layer.visible) {
		      overlay.addTo(map)
		    }
	    }
    })
  })
}

/**
 * Initializes leaflet map
 * @param div where map will be placed
 * @options initial centerpoint and zoomlevel
 * @returns the map
 */
function initMap (div, options, id) {
  var map = L.map(div, options)
  // assign id to map
  map.id = id

  const basePane = map.createPane('basePane')
  basePane.style.zIndex = 100

  var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    pane: 'basePane'
  })

  var roads = L.gridLayer.googleMutant({
    type: 'roadmap', // valid values are 'roadmap', 'satellite', 'terrain' and 'hybrid'
    pane: 'basePane'
  })

  var terrain = L.gridLayer.googleMutant({
    type: 'terrain', 
    pane: 'basePane'
  })

  var satellite = L.gridLayer.googleMutant({
    type: 'satellite', 
    pane: 'basePane'
  })

  var topo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri',
    pane: 'basePane'
  })

  var imagery = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri',
    pane: 'basePane'
  })

  const baseMaps = { Openstreetmap: osm, 'Google maps': roads, 'Google satellite': satellite, 'Terrain': terrain, 'ESRI topo': topo, 'ESRI satellite': imagery }
  const overlayMaps = {}
  map.layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map)

  if (!restoreMap(map)) {
    // use default map
    osm.addTo(map)
  }

  restoreBounds(map)

  L.control.scale({position:'bottomleft'}).addTo(map);
  
  map.on('baselayerchange', function (e) { changeBaseLayer(e) })
  map.on('zoomend', function () { saveBounds(map) })
  map.on('moveend', function () { saveBounds(map) })
  theMap = map
  return map
}
