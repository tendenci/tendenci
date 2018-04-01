jQuery(function($) {
	var previousChoice;

	$('.position_field').focus(function() {
		previousChoice = $(this).val();
	}).change(function() {
		var fieldID = $(this).attr('id');
		var newChoice = $(this).val();
		$('.position_field').each(function() {
			if ($(this).attr('id') !== fieldID && $(this).val() === newChoice) {
				$(this).find('option').each(function() {
					if ($(this).val() === previousChoice) {
						$(this).attr('selected', 'selected');
					}
					else {
						$(this).removeAttr('selected');
					}
				});
				return false;
			}
		});
		previousChoice = newChoice;
	});
});
