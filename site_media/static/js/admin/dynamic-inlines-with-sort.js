jQuery(function($) {
    $('div.inline-group').sortable({
        containment: 'parent',
        items: 'div.inline-related',
        handle: 'h3:first, .collapse-label',
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

    // function: toggle label field
    var manage_label_field = function(){
    	var selected_value = $(this).find(":selected").val();
    	var selected_text = $(this).find(":selected").text();
    	var fieldset = $(this).parents("fieldset");

    	// toggle label field
    	if (selected_value == "description"){
            fieldset.find(".label").hide();
    	}
    	else {
    		fieldset.find(".label").show();
    	}
    };

    // function: toggle description field
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
    };

    // function: toggle choice field
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
    };

    // function; hide all fields (display label)
    var hide_fields = function(){

        $(this).children().hide();

        var last_field = $(this).find("fieldset").children().last();
        last_field.prepend('<div class="done-btn">I am Done Here. Collapse.</div>') // done link

        var label = $(this).find("label").next().val(); // get label
        $(this).prepend('<div class="collapse-label">' + label + '</div>'); // show label
    };

    // function: expand_field_options
    var expand_field_options = function(){

//        var sorting = $(this).parents(".inline-group").find(".ui-sortable-placeholder");
//        console.log(sorting)
//        if(sorting) return false;

        $(this).siblings().show(); // show original markup
        $(this).hide();
    }

    // function: collapse field options
    var collapse_field_options = function(){
        var parent = $(this).parents(".dynamic-fields");
        parent.children().hide(); // hide original markup
        parent.find(".collapse-label").show(); // show label
    }

    /* called immediately; hiding and event-binding
    --------------------------------------------------------------------------------- */

    // bind change event to dropdown
    $("div.inline-group .field_type select")
        // each() handles initial calls; live() binds the change-event to f()
        .each(manage_label_field).live('change', manage_label_field)
        .each(manage_description_field).live('change', manage_description_field)
        .each(manage_choice_field).live('change', manage_choice_field);

    // hide dynamic field fields
    $(".dynamic-fields").each(hide_fields)

    // bind click event to label
    $(".collapse-label").live("click", expand_field_options);
    // bind click event to done-button
    $(".done-btn").live("click", collapse_field_options);

});
