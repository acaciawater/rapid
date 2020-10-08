/**
 * Update server versions when selected server type
 */
(function($) {
	$(document).ready(function() {
		$("#id_service_type").change(function () {
			  const $sel = $(this).find('option:selected');
			  const val = $sel.val();
			  const ref = $sel.text();
			  if (confirm(`Changing the service type to ${ref} will remove all layers.\nDo you really want this?.`)) {
				  // do something
				  const all = $(this).find('optgroup').hide()
				  const groups = $(this).find(`optgroup[label="${ref}"]`).show()
			  }
		})
	})
})(jQuery);