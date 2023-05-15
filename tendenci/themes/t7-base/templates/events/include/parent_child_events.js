// Toggle showing list of parent events based on event relationship on load
toggle_parents($('#id_event_relationship').val());

// Show list of parent events if this is a child event. Hide if this
// is a parent event
function toggle_parents(relationship) {
    var parent_events =  $('#id_parent').parent().parent();
    if (relationship == 'parent') {
        parent_events.hide();
        $('#id_parent').val('');
        toggle_repeat($('#id_parent').val());
    } else {
        parent_events.show();
    }
}

// Show list of child events that can be selected to indicate this
// child event should be a 'repeat of' if parent is selected. Toggle off
// if no parent is selected
toggle_repeat($('#id_parent').val());

function toggle_repeat(has_parent) {
    var repeat_of =  $('#id_repeat_of').parent().parent();
    if(has_parent) {
        repeat_of.show();
    } else {
        repeat_of.hide();
        $('#id_repeat_of').val('');
    }
}

// Show parent events if this is a child event
$('#id_event_relationship').on('change', function() {
    toggle_parents($('#id_event_relationship').val());
});

// Show 'repeat of' if Parent event selected
$('#id_parent').on('change', function() {
    toggle_repeat($('#id_parent').val());
});

// If 'repeat_of' selected, disable everything else
$('#id_repeat_of').on('change', function() {
    if ($(this).val()) {
        $('form :input:not(#id_repeat_of, button, [name=csrfmiddlewaretoken])').prop('disabled', true);
        $('.form-group').hide();
        $('legend').hide();
        $('.speaker_formset').hide();
        $('.formset-add').hide();
        toggle_repeat(true);
        $('button').parent().parent().show();
    } else {
        $('form :input:not(#id_repeat_of, button)').prop('disabled', false);
        $('.form-group').show();
    }
});
