// Toggle showing list of parent events based on event relationship on load
var allow_guests = $('#id_regconf-allow_guests');
var guest_limit = $('#id_regconf-guest_limit');
var require_guests_info = $('#id_regconf-require_guests_info');

toggle_guests();

// Show list of parent events if this is a child event. Hide if this
// is a parent event
function toggle_guests() {
    var checked = allow_guests.is(':checked') && $('#id_regconf-enabled').is(':checked');

    if (checked) {
        guest_limit.parent().parent().show();
        require_guests_info.parent().parent().parent().parent().show();
    } else {
        allow_guests.prop('checked', false);
        guest_limit.parent().parent().hide();
        require_guests_info.parent().parent().parent().parent().hide();
        guest_limit.val(0);
    }
}

// If 'repeat_of' selected, disable everything else
allow_guests.on('change', function() {
    toggle_guests();
});
