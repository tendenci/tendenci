$(document).ready(function(){
    if ($("#id_allow_anonymous_view").length > 0) {
        if ($("#id_allow_anonymous_view:checked").length == 1) {
            $('fieldset.permissions .form-field:not(fieldset.permissions .form-field:first)').hide();

            if($('fieldset.permissions > .form-field').length > 1) {
                $('fieldset.permissions .form-field:first').append('<a id="adv-perms" href="#id_allow_anonymous_view">+ Show Advanced Permissions</a>');
            }
        } else {
            if($('fieldset.permissions > .form-field').length > 1) {
                $('fieldset.permissions .form-field:first').append('<a id="adv-perms" href="#id_allow_anonymous_view">- Hide Advanced Permissions</a>');
            }
        }
        $('#adv-perms').click(function() {
            $('fieldset.permissions .form-field:not(fieldset.permissions .form-field:first)').slideToggle('fast');
             if ($('#adv-perms').text() == '- Hide Advanced Permissions') {
                $('#adv-perms').text('+ Show Advanced Permissions');}
            else {$('#adv-perms').text('- Hide Advanced Permissions');}
        });
        $('#id_allow_anonymous_view').click(function() {
            if ($("#id_allow_anonymous_view:checked").length == 1) {
                $('fieldset.permissions .form-field:not(fieldset.permissions .form-field:first)').slideUp('fast');
                $('#adv-perms').text('+ Show Advanced Permissions');
            } else {
                $('fieldset.permissions .form-field:not(fieldset.permissions .form-field:first)').slideDown('fast');
                $('#adv-perms').text('- Hide Advanced Permissions');
            }
        });
    }

    $("#admin-bar ul li").has(".sub").not('#themecolor').hover(function(){
        $(this).children(".sub").addClass('active');
    }, function() {
        $(this).children(".sub").removeClass('active');
    });
    $("#user-bar li").has(".sub").hover(function(){
        $(this).children(".sub").addClass('active');
    }, function() {
        $(this).children(".sub").removeClass('active');
    });

});
