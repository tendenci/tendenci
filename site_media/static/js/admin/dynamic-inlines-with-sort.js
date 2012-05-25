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

        if($(this).text() == 'Collapse'){
            collapse($(this));
        }else{
            expand($(this));
        }

    };

    var in_list = function(v, l){
        return (l.indexOf(v) >= 0)
    }

    var hide_triggers = [
        '',
        'header',
        'horizontal-rule'
    ]

    var manage_choice_field = function(){
        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

        extra_hide_triggers = ['choose-from-list','multi-select']
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

    	// toggle choices field
    	if (in_list(selected_value, extra_hide_triggers)){
            fieldset.find(".choices").show("fast");
    	}
    	else {
    		fieldset.find(".choices").hide("fast");
    	}
    };

    var manage_help_text = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

        extra_hide_triggers = ['description', 'horizontal-rule', 'header']
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

    	// toggle help text field 
        if (in_list(selected_value, extra_hide_triggers)){
            fieldset.find(".help_text").hide("fast");
    	}
    	else {
    		fieldset.find(".help_text").show("fast");
    	}

    }

    var manage_default_value = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

        extra_hide_triggers = ['check-box','file-uploader','description', 'horizontal-rule', 'header']
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

    	// toggle default value field
        if (in_list(selected_value, extra_hide_triggers)){
            fieldset.find(".default_value").hide("fast");
    	}
    	else {
    		fieldset.find(".default_value").show("fast");
    	}

    }
    
    var manage_special_functionality = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");

        extra_hide_triggers = ['check-box']
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

    	// toggle the special functionality and group fields
        if (in_list(selected_value, extra_hide_triggers)){
            fieldset.find(".field_function").show("fast");
            fieldset.find(".function_params").show("fast");
    	}
    	else {
    		fieldset.find(".field_function").hide("fast");
    		fieldset.find(".function_params").hide("fast");
    	}

    }

    var manage_required_checkbox = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");
        var element = fieldset.find('.required input[id$="required"]').parent();

        extra_hide_triggers = []
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

    	// toggle the required checkbox
    	if (in_list(selected_value, hide_triggers)){
            element.hide("fast");
    	}
    	else {
    		element.show("fast");
    	}

    }

    var manage_unique_checkbox = function(){

        var $dd = $(this); // drop-down
    	var selected_value = $dd.find(":selected").val();
    	var selected_text = $dd.find(":selected").text();
    	var fieldset = $dd.parents("fieldset");
        var element = fieldset.find('.unique input[id$="unique"]').parent();


        var hide_triggers = ['text','paragraph-text','email'];
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

    	// toggle the unique checkbox
        if (in_list(selected_value, hide_triggers)){
            element.show("fast");
    	}
    	else {
    		element.hide("fast");
    	}
    }

    var manage_admin_checkbox = function(){

        var $dd = $(this); // drop-down
        var selected_value = $dd.find(":selected").val();
        var selected_text = $dd.find(":selected").text();
        var fieldset = $dd.parents("fieldset");
        var element = fieldset.find('.admin_only input[id$="admin_only"]').parent();

        console.log('fieldset',fieldset)
        console.log('element',element);

        var hide_triggers = [];
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

        // toggle the admin only checkbox
        if (in_list(selected_value, hide_triggers)){
            element.hide("fast");
        }
        else {
            element.show("fast");
        }
    }

    var manage_exportable_checkbox = function(){

        var $dd = $(this); // drop-down
        var selected_value = $dd.find(":selected").val();
        var selected_text = $dd.find(":selected").text();
        var fieldset = $dd.parents("fieldset");
        var element = fieldset.find('.exportable input[id$="exportable"]').parent();

        extra_hide_triggers = []
        all_hide_triggers = hide_triggers.concat(extra_hide_triggers)

        if (in_list(selected_value, hide_triggers)){
            element.hide("fast");
        }
        else {
            element.show("fast");
        }

    }

    // bind change event to dropdown
    $("div.inline-group .field_type select")
        // each() handles initial calls; live() binds the change-event to future calls
        .each(manage_choice_field).live('change', manage_choice_field)
        .each(manage_help_text).live('change', manage_help_text)
        .each(manage_default_value).live('change', manage_default_value)
        .each(manage_special_functionality).live('change', manage_special_functionality)
        .each(manage_required_checkbox).live('change', manage_required_checkbox)
        .each(manage_unique_checkbox).live('change', manage_unique_checkbox)
        .each(manage_admin_checkbox).live('change', manage_admin_checkbox)
        .each(manage_exportable_checkbox).live('change', manage_exportable_checkbox);

});
