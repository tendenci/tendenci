jQuery(function($) {
    $('div.inline-group').sortable({
        containment: 'parent',
        items: 'div.inline-related',
        handle: 'h3:first',
        update: function() {
            $(this).find('div.inline-related').each(function(i) {
//                if ($(this).find('input[id$=label]').val()) {
                    $(this).find('input[id$=position]').val(i+1);
//                }
            });
        }
    });
    $('div.inline-related h3').css('cursor', 'move');
    $('div.inline-related').find('input[id$=position]').parents('.form-row.position').hide();


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

    var add_collapse_link = function(){
        var last_field = $(this).find("fieldset").children().last();
        last_field.prepend('<div class="done-btn">Collapse</div>')
    }

    var collapse = function(self){
        var label = self.parent().siblings(':first')

        //$(this).parent().parent().siblings().hide('slideUp');

        var fields = self.parent().parent().children();

        fields.each(function(index, value){
            var $value = $(value);
            if(!$value.hasClass('label') && !$value.hasClass('position')){
                $value.hide('fast');
            }
        })

        self.text('Expand');
    };

    var expand = function(self){
        var fields = self.parent().parent().children();
        fields.show('fast');
    };

    var toggle_handler = function(){

        console.log('toggle!');
        console.log($(this));

        if($(this).text() == 'Collapse'){
            collapse($(this));
        }else{
            expand($(this));
        }

    };

    // function: toggle choices field
    var manage_choice_field = function(){
        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

    	// toggle choices field
    	if (selected_value == "choose-from-list" || selected_value == "multi-select"){
            fieldset.find(".choices").show("fast");
    	}
    	else {
    		fieldset.find(".choices").hide("fast");
    	}
    };

    // function: toggle help-text field
    var manage_help_text = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

    	// toggle the
    	if (selected_value == "header" || selected_value == "description" || selected_value == "horizontal-rule"){
            fieldset.find(".help_text").hide("fast");
    	}
    	else {
    		fieldset.find(".help_text").show("fast");
    	}

    }

    // function: toggle default-value field
    var manage_default_value = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

    	// toggle the
    	if (selected_value == "check-box" || selected_value == "file-uploader" || selected_value == "header" || selected_value == "description" || selected_value == "horizontal-rule"){
            fieldset.find(".default_value").hide("fast");
    	}
    	else {
    		fieldset.find(".default_value").show("fast");
    	}

    }

    // function: toggle required checkbox
    var manage_required_checkbox = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

    	// toggle the
    	if (selected_value == "check-box" || selected_value == "header" || selected_value == "description" || selected_value == "horizontal-rule"){
            fieldset.find('.required input[id$="required"]').parent().hide("fast");
    	}
    	else {
    		fieldset.find('.required input[id$="required"]').parent().show("fast");
    	}

    }

    // function: toggle unique checkbox
    var manage_unique_checkbox = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

    	// toggle the
    	if (selected_value == "text" || selected_value == "paragraph-text" || selected_value == "email"){
            fieldset.find('.unique input[id$="unique"]').parent().show("fast");
    	}
    	else {
    		fieldset.find('.unique input[id$="unique"]').parent().hide("fast");
    	}
    }

    /* called immediately; hiding and event-binding
    --------------------------------------------------------------------------------- */

    // bind change event to dropdown
    //$("div.inline-group .field_type select")
        // each() handles initial calls; live() binds the change-event to f()
        //.each(manage_label_field).live('change', manage_label_field)
        //.each(manage_description_field).live('change', manage_description_field)
        //.each(manage_choice_field).live('change', manage_choice_field);

    // bind change event to dropdown
    $("div.inline-group .field_type select")
        // each() handles initial calls; live() binds the change-event to future calls
        .each(manage_choice_field).live('change', manage_choice_field)
        .each(manage_help_text).live('change', manage_help_text)
        .each(manage_default_value).live('change', manage_default_value)
        .each(manage_required_checkbox).live('change', manage_required_checkbox)
        .each(manage_unique_checkbox).live('change', manage_unique_checkbox);

    // create collapse-link
    //$('.dynamic-fields').each(add_collapse_link)

    // bind click event to collapse-link
    //$('.done-btn').live('click', toggle_handler)

    // bind click event to expand-link


    // hide dynamic field fields
    //$(".dynamic-fields").each(hide_fields)

    // bind click event to label
    //$(".collapse-label").live("click", expand_field_options);
    // bind click event to done-button
    //$(".done-btn").live("click", collapse_field_options);

});
