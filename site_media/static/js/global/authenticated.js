$(document).ready(function(){
    if ($("#id_allow_anonymous_view").length > 0) {
        if ($("#id_allow_anonymous_view:checked").length == 1) {
            $('fieldset.permissions .form-field:not(fieldset.permissions .form-field:first)').hide();
            $('fieldset.permissions').append('<a id="adv-perms" href="#id_allow_anonymous_view">Show Advanced Permissions</a>');
        } else {
            $('fieldset.permissions').append('<a id="adv-perms" href="#id_allow_anonymous_view">Hide Advanced Permissions</a>');
        }
        $('#adv-perms').click(function() {
            $('fieldset.permissions .form-field:not(fieldset.permissions .form-field:first)').slideToggle('fast');
             if ($('#adv-perms').text() == 'Hide Advanced Permissions') {
                $('#adv-perms').text('Show Advanced Permissions');}
            else {$('#adv-perms').text('Hide Advanced Permissions');}
        });
    }
});
