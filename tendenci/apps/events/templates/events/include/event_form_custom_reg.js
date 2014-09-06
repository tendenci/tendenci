$(document).ready(function() {

    // for custom registration form options
    var reg_enabled_checkbox = $('input#id_regconf-enabled'),
        discount_eligible_box = $('.id_regconf-discount_eligible'),
        use_custom_reg_checkbox = $('#use-custom-reg-checkbox input[type=checkbox]'),
        user_custom_reg_block = $('.id_regconf-use_custom_reg'),
        pricing_reg_forms = $(".regconfpricing_formset div[class$='reg_form']"),
        one_or_separate_form_block = $('#one-or-separate-form'),
        one_or_saparate_input_radio_labels = $('#one-or-separate-form label'),
        one_or_separate_input_radios = $('#one-or-separate-form input[type="radio"]');


    {% if not MODULE_EVENTS_CUSTOMREGFORMENABLED  %}
        user_custom_reg_block.hide();
        pricing_reg_forms.hide();
    {% else %}

    var disable_separate_forms = function(){
        //one_or_separate_input_radios[1].disabled=true;
       // $(one_or_saparate_input_radio_labels[1]).css({'color': '#aaa'});
    }

    {# disable the separate custom reg form option per pricing if not already selected #}
    {# We are going to permanently remove this option, but for now just disable it. #}
    {# 0 - separate form, 1 - one form #}
    if ( reg_enabled_checkbox.is(':checked') &&
          use_custom_reg_checkbox.is(':checked') &&
          one_or_separate_input_radios.filter(':checked').val() == '0')
    {

        {% if MODULE_EVENTS_ANONYMOUSMEMBERPRICING %}
        disable_separate_forms();
        {% endif %}
    }
    else{
        disable_separate_forms();
        pricing_reg_forms.hide();
    }

    var toggle_pricing_reg_form = function(){
        {# separate form for each pricing #}
        if (one_or_separate_input_radios.filter(':checked').val() == '1'){
            pricing_reg_forms.hide();
        }else{
            pricing_reg_forms.show();
        }
    }

    var toggle_use_custom_reg_options = function(){
        if (use_custom_reg_checkbox.is(':checked')){
            one_or_separate_form_block.show();
            toggle_pricing_reg_form();
        }else{
            one_or_separate_form_block.hide();
            pricing_reg_forms.hide();
        }
    }

    var toggle_custom_reg_form = function(){
        if (reg_enabled_checkbox.is(':checked')){
            discount_eligible_box.show();
            if (!$("#id_is_recurring_event").is(':checked')) {
                user_custom_reg_block.show();
                toggle_use_custom_reg_options();
            }else {
                use_custom_reg_checkbox.attr('checked', false);
                user_custom_reg_block.hide();
                pricing_reg_forms.hide();
            }
        }else{
            use_custom_reg_checkbox.attr('checked', false);
            user_custom_reg_block.hide();
            pricing_reg_forms.hide();
            discount_eligible_box.hide();
        }
    }

    toggle_custom_reg_form();


    reg_enabled_checkbox.click(function () {
          toggle_custom_reg_form();
    });

    use_custom_reg_checkbox.click(function () {
          toggle_use_custom_reg_options();
    });

    one_or_separate_input_radios.click(function () {
          toggle_pricing_reg_form();
    });

 {% endif %}

    var toggle_email_reminder = function(item){
        if (item.is(':checked')){
            $(item).closest('div.form-field').next().show();
        }else{
            $(item).closest('div.form-field').next().hide();
        }
    }

    var email_reminder = $('input[id=id_regconf-send_reminder]');
    toggle_email_reminder(email_reminder);
    email_reminder.click(function(){
        var $this = $(this);
        toggle_email_reminder($this);
    });

    if ($("#id_display_event_registrants").is(':checked')) {
        //$('fieldset.attendees .form-field:not(fieldset.attendees .form-field:first)').show();
        $('div.id_display_registrants_to').parent().show();
    }else {
        //$('fieldset.attendees .form-field:not(fieldset.attendees .form-field:first)').hide();
        $('div.id_display_registrants_to').parent().hide();
    }
    $('#id_display_event_registrants').click(function(){
        if($("#id_display_event_registrants").is(':checked')){
            //$('fieldset.attendees .form-field:not(fieldset.attendees .form-field:first)').slideDown('fast');
            $('div.id_display_registrants_to').parent().slideDown('fast');
        }else{
            //$('fieldset.attendees .form-field:not(fieldset.attendees .form-field:first)').slideUp('fast');
            $('div.id_display_registrants_to').parent().slideUp('fast');
        }
    });

    var recurringCheck = $('#id_is_recurring_event');
    var repeatFreq = $('.form-field .id_frequency');
    var repeatType = $('.form-field .id_repeat_type');
    var recurOn = $('.form-field .id_recurs_on');
    var endRecurring = $('.form-field .id_end_recurring');
    var repeatValue = repeatType.find('select#id_repeat_type');

    if (recurringCheck.is(':checked')) {
        repeatFreq.show();
        repeatType.show();
        endRecurring.show();
    }else {
        repeatFreq.hide();
        repeatType.hide();
        endRecurring.hide();
    }
    // Hide Recurs On field when 'Daily' or 'Weekly' types are selected
    if ((repeatValue.val() == 3) || (repeatValue.val() == 4)) {
        recurOn.show();
    }else {
        recurOn.hide();
    }

    recurringCheck.click(function(){
        if(recurringCheck.is(':checked')){
            repeatFreq.slideDown('fast');
            repeatType.slideDown('fast');
            endRecurring.slideDown('fast');
            if ((repeatValue.val() == 3) || (repeatValue.val() == 4)) {
                recurOn.slideDown('fast');
            }
            toggle_custom_reg_form();
        }else{
            repeatFreq.slideUp('fast');
            repeatType.slideUp('fast');
            recurOn.slideUp('fast');
            endRecurring.slideUp('fast');
            toggle_custom_reg_form();
        }
    });
    repeatValue.change(function(){
        if (($(this).val() == 3) || ($(this).val() == 4)) {
            recurOn.slideDown('fast');
        }else {
            recurOn.slideUp('fast');
        }
    });
});
