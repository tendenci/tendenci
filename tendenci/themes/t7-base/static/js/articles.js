$(document).ready(function(){
	$('#id_date').datepicker({ dateFormat: "yy-mm-dd" });

	function check_category() {
		if( $('#id_search_category').val() == "featured" || $('#id_search_category').val() == "syndicate" ) {
			$('#id_q').attr('disabled', 'disabled');
			$('#id_q').val('');
		} else {
			$('#id_q').prop('disabled', false );
		}
	}

	function check_filter_date() {
		if( !$('#id_filter_date').is(':checked') ) {
			$('#id_date').attr('disabled', 'disabled');
			$('#id_date').val('');
		} else {
			$('#id_date').prop('disabled', false );
		}
	}

	check_category();
	check_filter_date();

	$('#id_search_category').on("change", function(){
		check_category();
	});

	$('#id_filter_date').on("change", function(){
		check_filter_date();
	});
});
