// Update pricing end dates for every event end date change
$("#id_end_dt_0").on("change", function() {
    var value = $("#id_end_dt_0").val();
    var date = updateDate(value, -1)

    // set new date value for every pricing form
    $(".regconfpricing_formset").each(function() {
    	var start_dt_node = $(this).find(".datepicker").first();
    	var start_dt = new Date($(start_dt_node).val());
    	var date_obj = new Date(date);
    	if (start_dt > date_obj){
    		$(start_dt_node).val(date);
    	}
        $(this).find(".datepicker").last().val(date);
    });
});

// Update end date to be similar to start date
$("#id_start_dt_0").on("change", function() {
    var value = $("#id_start_dt_0").val();
    $("#id_end_dt_0").val(value);
    $("#id_end_dt_0").change();
});

// Update end time to be 2 hours after to start time
$("#id_start_dt_1").on("change", function() {
    var value = $("#id_start_dt_1").val();
    var time = value.split(" ");
    var format = time[1];

    var hm = time[0].split(":");
    var minute = hm[1];
    var hour = parseInt(hm[0], 10);

    if (hour === 12) {
        hour -= 12;
    }
    hour += 2;
    if (hour >= 12) {
        if (hour > 12) {
            hour -= 12;
        }
        if (format === 'AM') {
            format = 'PM';
        } else {
            format = 'AM';
            var newDate = updateDate($("#id_end_dt_0").val(), 1);
            $("#id_end_dt_0").val(newDate);
            $("#id_end_dt_0").change();
        }
    }

    // recreate string
    if (hour < 10) {
        hour = '0' + hour;
    }
    var newVal = hour + ':' + minute + ' ' + format;
    $("#id_end_dt_1").val(newVal);
});

function updateDate(value, offset) {
    var date = value.split("-");
    // add 1 day
    date = new Date(date[0], parseInt(date[1],10)-1, parseInt(date[2],10)+offset);

    // recreate string
    var newVal = date.getFullYear() + "-";
    var month = date.getMonth() + 1;
    var day = date.getDate();
    if (month < 10) {
        newVal += '0' + month + "-";
    }else {
        newVal += month + "-";
    }
    if (day < 10) {
        newVal += '0' + day;
    }else {
        newVal += day;
    }
    return newVal;
}
