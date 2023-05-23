(function($) {
	$(document).ready(function () {
		var action_field = $("form#changelist-form").find('select[name=action]');
		var cert_field = $("form#changelist-form").find('select[name=cert]');
		$(cert_field).hide();
		$(action_field).change(function(){
			if ($(this).val() == "assign_cert_track_to_selected"){
				$(cert_field).show();
			}else{
				$(cert_field).hide();
			}
		});
	});	
}(jQuery));
