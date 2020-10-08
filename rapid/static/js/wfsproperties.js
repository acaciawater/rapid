/**
 * Update property selector when selected layer changes
 */
(function($) {
	$(document).ready(function() {
		$("#id_layer").change(function (evt) {
			  const val = $(this).find('option:selected').val()
			  if (val > 0) {
				  const prop = $('#id_property option:selected').val()
				  $.getJSON(`/ows/props/${val}`).then(response => {
					  // console.debug(response.layer)
					  // remove all options but the first
					  $('#id_property option:gt(0)').remove();
					  const $el = $('#id_property') 
					  Object.keys(response.layer.properties).forEach(p => $el.append(`<option>${p}</option>`))
					  $el.val(prop)
				  })
			  }
		})
	})
})(jQuery);