$(document).ready(function(){
    if ($("#id_allow_anonymous_view").length > 0) {
        if ($("#id_allow_anonymous_view:checked").length == 1) {
            $('fieldset.permissions .form-group:not(fieldset.permissions .form-group:first)').hide();

            if($('fieldset.permissions > .form-group').length > 1) {
                $('fieldset.permissions .form-group:first').append('<a id="adv-perms" href="#id_allow_anonymous_view">+ Show Advanced Permissions</a>');
            }
        } else {
            if($('fieldset.permissions > .form-group').length > 1) {
                $('fieldset.permissions .form-group:first').append('<a id="adv-perms" href="#id_allow_anonymous_view">- Hide Advanced Permissions</a>');
            }
        }
        $('#adv-perms').on("click", function() {
            $('fieldset.permissions .form-group:not(fieldset.permissions .form-group:first)').slideToggle('fast');
             if ($('#adv-perms').text() == '- Hide Advanced Permissions') {
                $('#adv-perms').text('+ Show Advanced Permissions');}
            else {$('#adv-perms').text('- Hide Advanced Permissions');}
        });
        $('#id_allow_anonymous_view').on("click", function() {
            if ($("#id_allow_anonymous_view:checked").length == 1) {
                $('fieldset.permissions .form-group:not(fieldset.permissions .form-group:first)').slideUp('fast');
                $('#adv-perms').text('+ Show Advanced Permissions');
            } else {
                $('fieldset.permissions .form-group:not(fieldset.permissions .form-group:first)').slideDown('fast');
                $('#adv-perms').text('- Hide Advanced Permissions');
            }
        });
    }

    $("#admin-bar ul li").has(".sub").not('#themecolor').on('mouseenter', function(){
        $(this).children(".sub").addClass('active');
    }).on('mouseleave', function() {
        $(this).children(".sub").removeClass('active');
    });
    $("#user-bar li").has(".sub").on('mouseenter', function(){
        $(this).children(".sub").addClass('active');
    }).on('mouseleave', function() {
        $(this).children(".sub").removeClass('active');
    });

});
