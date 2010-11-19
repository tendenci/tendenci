jQuery(function($) {
    $('div.inline-group').sortable({
        containment: 'parent',
        items: 'div.inline-related',
        handle: 'h3:first',
        update: function() {
            $(this).find('div.inline-related').each(function(i) {
                if ($(this).find('input[id$=label]').val()) {
                    $(this).find('input[id$=position]').val(i+1);
                }
            });
        }
    });
    $('div.inline-related h3').css('cursor', 'move');
    $('div.inline-related').find('input[id$=position]').parent('div').hide();

    //    text
    //    paragraph
    //    check-box
    //    choose-from-list
    //    multi-select
    //    email-field
    //    file-uploader
    //    date
    //    date-time
    //    membership-type
    //    payment-method
    //    first-name
    //    last-name
    //    email-header
    //    description
    //    horizontal-rule

        // description field function
    var manage_label_field = function(){
    	var selected_value = $(this).find(":selected").val();
    	var selected_text = $(this).find(":selected").text();
    	var fieldset = $(this).parents("fieldset");

    	// toggle description field
    	if (selected_value == "description"){
            fieldset.find(".label").hide();
    	}
    	else {
    		fieldset.find(".label").show();
    	}
    }

    // description field function
    var manage_description_field = function(){
    	var selected_value = $(this).find(":selected").val();
    	var selected_text = $(this).find(":selected").text();
    	var fieldset = $(this).parents("fieldset");

    	// toggle description field
    	if (selected_value == "description"){
            fieldset.find(".description").show();
    	}
    	else {
    		fieldset.find(".description").hide();
    	}
    }

    // choice field function
    var manage_choice_field = function(){
    	var selected_value = $(this).find(":selected").val();
    	var selected_text = $(this).find(":selected").text();
    	var fieldset = $(this).parents("fieldset");

    	// toggle choices field
    	if (selected_value == "choose-from-list" || selected_value == "multi-select"){
            fieldset.find(".choices").show();
    	}
    	else {
    		fieldset.find(".choices").hide();
    	}
    }

    // type-drop-down initial; type-drop-down change-event binding
    $("div.inline-group .field_type select")
        .each(manage_label_field).live('change', manage_label_field)
        .each(manage_description_field).live('change', manage_description_field)
        .each(manage_choice_field).live('change', manage_choice_field);

});
