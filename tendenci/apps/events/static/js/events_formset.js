function update_form_fields(form, original_form, form_number, total, remove) {
    form_number = parseInt(form_number);

    // edit page detection
    var href = window.location.href;
    var is_edit_page = (href.indexOf('/edit') > -1);
    var search = '-' + (form_number) + '-';

    var original_form_number = null;
    if (original_form) {
        original_form_number = original_form.find('input[name="form-number"]').val()
        search = '-' + (original_form_number) + '-';
    }

    var replacement = '-' + (form_number + 1) + '-';
    var rep_form_number = form_number + 1;

    if (is_edit_page) {
        replacement = '-' + (total) + '-';
        rep_form_number = total;
    } else {
        // update replacement according to removing
        // or adding an form
        if (remove) {
            replacement = '-' + (form_number - 1) + '-';
            rep_form_number = form_number - 1;
        }
    }
    // update the class attributes
    form.find('div[class]').each(function() {
        var _class= $(this).attr('class').replace(search, replacement);
        $(this).attr('class', _class);
    });

    // update the name attribute in each for input
    form.find(':input').each(function() {
        var name = $(this).attr('name').replace(search, replacement);
        var id = 'id_' + name;
        var type = $(this).attr('type');
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');

        if (type == 'checkbox') {
            $(this).removeAttr('value')
        }
    });

    // update the label attribute wrapped on each form input
    form.find('label').each(function() {
    	if ($(this).attr('for')){
	        var newFor = $(this).attr('for').replace(search, replacement);
	        var id = newFor;
	        if (newFor.indexOf('id_') < 0)
	            id = 'id_' + newFor;
	        $(this).attr('for', id);
       }
    });


    // remove mceEditor and display the textarea - because it doesn't work on clone
    if (!remove) {
        form.find('.mceEditor').each(function() {
            var $this = $(this);
            $this.parent('.field').find('textarea').show();
            $this.remove();
        });
    }

    // update the form field values with
    // the original forms
    if (original_form) {
        original_form.find('input[type="text"]').each(function() {
            var input_value = $(this).val();
            var name = $(this).attr('name').replace(search, replacement);
            form.find('input[name=' + name +']').val(input_value);
        });
    }

    // update the form number element
    form.find('input[name="form-number"]').val(rep_form_number);

    return form;
}

function clone_form(selector, type) {
    var current_element = $(selector);
    var new_element = current_element.clone(true);
    var form_functions = current_element.next();
    var form_functions_clone = form_functions.clone(true);
    var total = parseInt($('#' + type + '-TOTAL_FORMS').val());
    var form_number = current_element.find('input[name="form-number"]').val();
    // check if we have mceEditor
    var textarea_id;
    var myEditor = $(new_element).find('.mceEditor');
    if (myEditor){
        var mytextarea = myEditor.parent('.field').find('textarea');
        if (mytextarea){
            textarea_id = mytextarea.attr('id');
        }
    }

    new_element.find('input.datepicker').removeClass('hasDatepicker')

    new_element = update_form_fields(
        new_element,
        current_element,
        form_number,
        total,
        false
    );

    // update the total
    total++;
    $('#' + type + '-TOTAL_FORMS').val(total);

    // add the element to the dom
    new_element.hide();
    current_element.after(new_element);
    new_element.fadeIn(200);

    // Add mce Editor
    if (myEditor){
        if (textarea_id){
        var search = '-' + (form_number) + '-';
        var replacement = '-' + (parseInt(form_number) + 1) + '-';
        var new_textarea_id = textarea_id.replace(search, replacement);

        // it's weird, the new id has to add id_ in front of the original one
        // id_speaker-1-description
        if (new_textarea_id.substr(0, 3) !='id_'){
            new_textarea_id = 'id_' + new_textarea_id;
        }
        tinyMCE.execCommand('mceAddControl', false, new_textarea_id);
        tinyMCE.triggerSave();
      }
    }


    // make sure all forms can delete
    new_element.before(form_functions_clone);

    // enable the delete link for the next and previous form
    // and remove the add link on the previous
    if (total > 1) {
        var add_link = form_functions.find('div.formset-add');
        add_link.css({ display: 'inline' });

        var delete_link = form_functions.find('div.formset-delete');
        delete_link.css({ display: 'inline', marginLeft: '15px' });

        var prev_add_link = form_functions_clone.find('div.formset-add');
        prev_add_link.hide();

        var prev_delete_link = form_functions_clone.find('div.formset-delete');
        prev_delete_link.css({
            display: 'inline',
            marginLeft: '0px'
        });
    }
}

function delete_form(current_form, selector, type) {
    var current_form_number = current_form.find('input[name="form-number"]').val();

    // all visible next/prev forms
    var forms_prev = current_form.prevAll(selector + ':visible');
    var forms_after = current_form.nextAll(selector + ':visible');

    // prevous form information
    var prev_form_functions = current_form.prev('div.formset-functions:visible');
    var prev_form = prev_form_functions.prev(':visible');

    // form total
    var total = $('#' + type + '-TOTAL_FORMS').val();

    // edit page detection
    var href = window.location.href;
    var is_edit_page = (href.indexOf('/edit') > -1);

    var form_functions = prev_form_functions;
    // if its the last form this should execute on
    // the current form and not the previous
    if (form_functions.length == 0) {
        if (forms_after.length == 1) {
            form_functions = $(forms_after[0]).next();
        } else {
            form_functions = current_form.next();
        }
    }

    // decrement the management for total on add pages
    // only
    if (!is_edit_page) {
        total--;
        $('#' + type + '-TOTAL_FORMS').val(total);
    }

    // update the labels and inputs of the remaining forms
    if (!is_edit_page) {
        if (forms_after.length >= 1) {
            forms_after.each(function() {
                var form = $(this);
                var form_number = form.find('input[name="form-number"]').val();
                update_form_fields(form, null, form_number, total, true);
            });
        }
    };

    // adjust the links
    if ((forms_prev.length == 0) && (forms_after.length == 0)) {
        var delete_link = form_functions.find('div.formset-delete');
        delete_link.hide();
    }

    if ((forms_prev.length >= 1) && (forms_after.length == 0)) {
        var add_link = form_functions.find('div.formset-add');
        add_link.css({ display: 'inline' });

        var delete_link = form_functions.find('div.formset-delete');
        delete_link.css({ display: 'inline', marginLeft: '15px' });
    }

    if ((forms_prev.length == 0) && (forms_after.length == 1)) {
        var add_link = form_functions.find('div.formset-add');
        add_link.css({ display: 'inline' });

        var delete_link = form_functions.find('div.formset-delete');
        delete_link.hide();
    }

    // add the add link back
    if ((forms_prev.length == 1) && (forms_after.length == 0)) {
        var add_link = form_functions.find('div.formset-add');
        add_link.css({ display: 'inline' });

        var delete_link = form_functions.find('div.formset-delete');
        delete_link.hide();
    }


    // delete stuff differently depending on page
    // your on. ie. events/edit
    if (is_edit_page) {
        // append the magic hidden element for it to
        // be deleted
        delete_name = type + '-' + current_form_number + '-DELETE';
        delete_input = '<input type="hidden" name="' + delete_name + '" ';
        delete_input += 'id="id_' + delete_name + '" value="1" />';
        current_form.parent().prepend(delete_input);

        // delete the functions
        current_form.next().hide();

        // delete the form
        current_form.slideUp(400, function() {
            $(this).hide();
        });

    } else {
        // delete the functions
        current_form.next().remove();

        // delete the form
        current_form.slideUp(400, function() {
            $(this).remove();
        });
    }
}

function get_formset_and_prefix(o) {
    var href = o.attr("href").replace('#','');
    var form_set = href.split(',')[0];
    var prefix = href.split(',')[1].split('-')[0];

    return {
        form_set: form_set,
        prefix: prefix
    }
}

function initialize_pickers(){
    $(".datepicker").datepicker({ dateFormat: 'yy-mm-dd' });
    $(".timepicker").timepicker({'step':15});
}

function toogle_tax_rate_field(element) {
    if (element.is(':checked')) {
        element.parent().parent().parent().parent().next().show();
    } else {
        element.parent().parent().parent().parent().next().hide();
    }
}

function hook_all_tax_fields_js() {
    $("input[name$='include_tax']").each(function() {
        toogle_tax_rate_field($(this));
        $(this).click(function() {
            toogle_tax_rate_field($(this));
        });
    });
}

$(document).ready(function(){
    initialize_pickers();
    hook_all_tax_fields_js();
    var form_set_funcs = $('div.formset-functions')

    // hide the delete link if it's an add page
    var href = window.location.href;
    if (href.indexOf('/add') > -1) {
        form_set_funcs.find('div.formset-add').show();
        form_set_funcs.find('div.formset-delete').hide();
    }

    if (href.indexOf('/edit') > -1) {
        var fsa = form_set_funcs.find('div.formset-add');
        var fsd = form_set_funcs.find('div.formset-delete');

        // hide all the add links except for the last one
        fsa.each(function(i) {
            var e = $(this);
            var next_class = e.parent().next().attr('class');

            if (!next_class || next_class.indexOf('formset') == -1) {
                e.css({
                    display: 'inline'
                });
            } else {
                e.css({
                    display: 'none'
                });
            }
        });

        //hide the delete link if there is only one
        fsd.each(function(i) {
            var e = $(this);
            var prev_class = e.parent().prev().prev().attr('class');
            var next_class = e.parent().next().attr('class');

            if ((!next_class || next_class.indexOf('formset') == -1) &&
               (!prev_class || prev_class.indexOf('formset') == -1)) {
                e.hide();
            } else {
                e.css({
                    display: 'inline',
                    marginLeft: '15px'
                });
            }
        });
    }

    $('div.formset-add a').click(function(e) {
        var params = get_formset_and_prefix($(this));
        clone_form('div.' + params.form_set + ':visible:last', params.prefix);
        initialize_pickers();
        hook_all_tax_fields_js();
        e.preventDefault();
        //return false;
    });

    $('div.formset-delete a').click(function(e) {
        var params = get_formset_and_prefix($(this));
        var selector = 'div.' + params.form_set;
        var current_form = $(this).closest('div.formset-functions').prev();
        delete_form(current_form, selector, params.prefix);
        e.preventDefault();
        //return false;
    });
});