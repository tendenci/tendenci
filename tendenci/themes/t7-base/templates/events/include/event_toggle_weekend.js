function is_weekend(dt_str){
	var mydate = new Date(dt_str);
	mydate.setDate(mydate.getDate() + 1); // add 1 day because time is not specified when converted to date
	if(mydate.getDay() == 6 || mydate.getDay() == 0) {
		return true;
	}else{
	    return false;
	}
}

$(document).ready(function() {
	weekend = $('#id_on_weekend').closest('.form-group');
            start_dt = $('input#id_start_dt_0');
            start_dt_val = start_dt.val();
            end_dt =  $('input#id_end_dt_0');
            end_dt_val = end_dt.val();

            if(start_dt_val == end_dt_val && !is_weekend(start_dt_val)){
                weekend.hide();
            } else {
                weekend.show();
            }

            start_dt.on("change", function() {
            	console.log($(this).val() == end_dt_val);
            	console.log(!is_weekend($(this).val()));
            	end_dt_val = $('input#id_end_dt_0').val();
                if ($(this).val() == end_dt_val && !is_weekend($(this).val())) {
                    weekend.hide();
                } else {
                    weekend.show();
                }
            });

            end_dt.on("change", function() {
            	start_dt_val = $('input#id_start_dt_0').val();
            	console.log($(this).val() ==start_dt_val);
            	console.log(!is_weekend($(this).val()));
                if ($(this).val() == start_dt_val && !is_weekend($(this).val())) {
                    weekend.hide();
                } else {
                    weekend.show();
                }
            });
 });