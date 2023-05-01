// Toggle showing list of parent events based on event relationship on load
toggle_parents($('#id_event_relationship').val());

// Show list of parent events if this is a child event. Hide if this
// is a parent event
function toggle_parents(relationship) {
    var parent_events =  $('#id_parent').parent().parent();
    if (relationship == 'parent') {
        parent_events.hide();
        $('#id_parent').val('');
    } else {
        parent_events.show();
    }
}

// Show parent events if this is a child event
$('#id_event_relationship').on('change', function() {
    toggle_parents($('#id_event_relationship').val());
});
