//var price_quantity = {{ price.quantity }};
//var price_price = {{ price.price }};
var price_quantity = 1;
var price_price = 0;

function deleteRegistrant(ele, prefix) {
    var registrant_form = $(ele).parents('.registrant-form');
    var attr_id = $(registrant_form).attr("id");
    // remove the registrant form
    $(registrant_form).remove();
    // $(registrant_form).slideUp(600, function(){
        // $(this).remove();
    // });

    // update the TOTAL_FORMS
    var forms = $(".registrant-form");
    $("#id_" + prefix + "-TOTAL_FORMS").val(forms.length);

    // update the total amount and remove the reg price entry
    var reg_id = attr_id.split('_')[1];
    var reg_id_0 = reg_id-1;
    removeSummaryEntry(prefix, reg_id_0);

    // update form index
    var this_form;
    for (var i=0, formCount=forms.length; i<formCount; i++){
        this_form = forms.get(i);
        $(this_form).find(".form-field").children().children().each(function() {
            if (this){
                updateIndex(this, prefix, i);
            }
        });
        // update form header
        if (i > 0){
            updateFormHeader(this_form, prefix, i);
        }
    }

    return false;
}

function updateIndex(e, prefix, idx){
    var id_regex = new RegExp('(registrant-\\d+)');
    var replacement = prefix + '-' + idx
    if ($(e).attr("for"))
        {$(e).attr("for", $(e).attr("for").replace(id_regex, replacement));}
    if (e.id) {e.id = e.id.replace(id_regex, replacement);}
    if (e.name){ e.name = e.name.replace(id_regex, replacement);}
}

// update the serial number on the form. ex: Registrant #3, Reg #3
function updateFormHeader(this_form, prefix, idx){
    idx = idx + 1;

    // change the serial number on the form
    var id_regex = new RegExp('(registrant_\\d+)');
    var replacement = prefix + '_' + idx
    if (this_form.id) {this_form.id = this_form.id.replace(id_regex, replacement);}

    var reg_header = $(this_form).find('.registrant-header');
    if (reg_header) {
        $(reg_header).parent().children('div:last').show();
        $(reg_header).children('span.showhide').text('- ');
        var ic = $(reg_header).find('.item-counter');
        if (ic) {
            $(ic).html(idx);}
    };

};

function addRegistrant(ele, prefix, price) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('.registrant-form:first').clone(true).get(0);

    $('.registrant-form:first').find('.registrant-header').removeClass('hidden');
    //$(row).insertAfter($('.registrant-form:last')).find('.hidden').removeClass('hidden');
    // remove the error
    $(row).find('div.error').remove();

    {% if not event.require_guests_info  %}
    // remove required att
    $(row).find('div.label').removeClass("required");
    {% endif %}

    // update id attr
    var id_regex = new RegExp('(registrant_\\d+)');
    var replacement = prefix + '_' + formCount;
    if(row.id){
        row.id = row.id.replace(id_regex, replacement);
    }
    //$(row).find(".form-field").children().children().each(function() {
    $(row).find(".form-field").find('[id^="id_registrant"]').each(function() {
        updateIndex(this, prefix, formCount);
        var $this = $(this);
        if ($this.attr('type') == 'text'){
         $this.val('');
        }

        // uncheck the checkbox
        if ($this.attr('type') == 'checkbox'){
         $this.attr('checked', false);

         {% if request.user.is_superuser %}
        if ($this.attr('name').search('override') != -1)
        {
            var price_box = $this.closest('.admin-override').next();
            toggle_admin_override($this, price_box);
        }
         {% endif %}

        }

    });

    {% if event.registration_configuration.allow_free_pass %}
    $(row).find(".free-pass-message").html('');
    $(row).find(".fp-field input[type=checkbox]").attr('checked', false);
    $(row).find(".fp-field").hide();
    {% endif %}

    $(row).find(".form-field").find('label[for^="id_registrant"]').each(function() {
        updateIndex(this, prefix, formCount);
    });

    var price = $(row).find('.registrant-pricing:checked').next('strong').find('span').data('price');
    if (isNaN(price)){
        price = 0;
    }

    $(row).insertAfter($('.registrant-form:last')).find('.hidden').removeClass('hidden');

    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    updateFormHeader(row, prefix, formCount);
    updateSummaryEntry(prefix, formCount, price);

    $(row)[0].scrollIntoView();

    return false;
}

function add_registrants(e, prefix) {
    //extra_count = $(e).parent().find('.extra-registrants').val();
    //extra_count = parseInt(extra_count);
    extra_count = 1;
    if (extra_count > 0) {
        for(var i=0; i<extra_count; i++){
            addRegistrant(e, prefix, price_price);
        }
    }
    return false;
}

function add_registrant_set(e, prefix) {
    extra_count = price_quantity;
    if (extra_count > 0) {
        addRegistrant(e, prefix, false);
        for (var i=1; i<extra_count; i++) {
            addRegistrant(e, prefix, price_price);
        }
    }
    return false;
}

function get_registrant_pricing_obj($block){
    var $checked_price = $block.find('.registrant-pricing:checked'),
        $override = $block.find('.admin-override input:checked'),
        $override_price = $block.find('.admin-override_price input'),
        price = 0;

    if ($override.length > 0) {
        price = $override_price.val();
    } else if ($checked_price.length > 0) {
        price = $checked_price.next('strong').find('span').data('price');
    } else {
        return false;
    }

    if (isNaN(price)){
        price = 0;
    }

    //var id_regex = new RegExp('(registrant_(\\d+))');
    var myRegexp = /registrant-(\d+)/;
    var match = myRegexp.exec($checked_price.attr('name'));
    var idx = parseInt(match[1]);

    return {'idx': idx, 'price': price};
}

function populate_blank_fields(){
    // populate the blank fields in the forms below with the content from the first form.
    // get the first form
    var first_form = $('.registrant-form:first'),
        prefix = 'registrant';

    // get each text field from the form
    var regexp = /registrant-\d+-([\w\d_]+)/;
    var match, name, value;
    var myfields = {};
    $(first_form).find(".form-field").find('[id^="id_registrant"]').each(function() {
        var $this = $(this);
        //if ($this.attr('type') == 'text'){
            name = $this.attr('name');
            match = regexp.exec(name);
            if (match !== null){
                if (match[1] !== 'first_name' && match[1] !== 'last_name'){
                    myfields[match[1]] = $this.val();
                }
            }
       // }

    });

    if (!$.isEmptyObject(myfields)){
        var num_forms = $('.registrant-form:not(:first)').length;
        for (i=1; i<=num_forms; i++){
            $.each(myfields, function(name, value) {
                //var field = $('input[name=' + prefix + '-' + i + '-' + name + ']');
                var field = $('[name=' + prefix + '-' + i + '-' + name + ']');
                if(!$.trim($(field).val()).length) {
                    $(field).val(value);
                }
            });
        }
    }

}

{% if request.user.is_superuser %}
function toggle_admin_override(checkbox, price_box){
    if ($(checkbox).is(':checked')){
            //$(target).slideDown('fast');
            $(price_box).show();

        }else{
            //$(target).slideUp('fast');
            $(price_box).hide();
        }
}
{% endif %}

// get the form index from the string str
function get_idx(regexp, str){
    var match = regexp.exec(str);
    if (match !== null){
        return parseInt(match[1]);
    }

    return null
}

var name_regexp = /registrant-(\d+)/;

{% if not event.is_table and request.user.is_superuser %}
function override_update_summary_entry(prefix, registrant_form){
    // update the summary entry whenever the override checkbox is clicked
    // or the override input field is changed.
    var input_box, idx, price, name_attr;
    var override = true;

    var override_node = $(registrant_form).find('.admin-override'),
        override_price_node = $(registrant_form).find('.admin-override_price');
    // if override is checked, find the value of the input
    if ($($(override_node).find('input[type=checkbox]:checked')).length > 0){
        input_box = $(override_price_node).find('input[type=text]');

        name_attr = $(input_box).attr('name');
        idx = get_idx(name_regexp, name_attr);
        price = parseInt($(input_box).val());

        if (isNaN(price)){
            override = false;
        }

    }
    else{
        override = false;
    }

    if (!override){
        var this_pricing = $(registrant_form).find('.registrant-pricing');
        name_attr = $(this_pricing).eq(0).attr('name');
        idx = get_idx(name_regexp, name_attr);
        var pricing_obj = get_registrant_pricing_obj($(registrant_form));
        if (pricing_obj == false ){
            price = 0;
        }else{
            price = pricing_obj.price;
        }
    }
    updateSummaryEntry(prefix, idx, price);
}
{% endif %}

{% if event.is_table and request.user.is_superuser %}
function table_override_update_summary_entry(prefix, override, override_price){
    var input_box, idx, price_first, price, diff;
    var num_items = $('.summary-'+ prefix).length;

    if (override){
        // price = (override_price/num_items).toFixed(2);
        // diff = override_price - num_items * parseFloat(price);
        // if (diff != 0){
            // price_first = (parseFloat(price) + diff).toFixed(2);
        // }else{
            // price_first = price;
        // }

        updateSummaryEntry(prefix, 0, override_price);
        // updateSummaryEntry(prefix, 0, price_first);
//
        // for (var i=1; i<num_items; i++){
            // updateSummaryEntry(prefix, i, price);
        // }

    }else{
        //for (var i=0; i<num_items; i++){
        price = $('#summary-registrant-0').find('.item-price').data('price');
        updateSummaryEntry(prefix, 0, price);
        //}
    }
}
{% endif %}

$(document).ready(function(){
    var prefix = 'registrant';

    // show delete-button-wrap
    $(".delete-button-wrap").show();
    // delete confirmation
    $('button.delete-button').on('click', function(e){
         var delete_confirm = confirm('Are you sure you want to delete this registrant?');   // confirm
         if(delete_confirm) {
            deleteRegistrant(this, 'registrant');
         }
        return false;   // cancel
    });
    $('.registrant-header').click(function() {
        $(this).parent().children('div:last').toggle();
        if ($(this).children('span.showhide').text() == "+ ") {
            $(this).children('span.showhide').text('- ');
        } else
        {$(this).children('span.showhide').text('+ '); }
    });




    {% if not event.is_table %}
    $('.registrant-pricing').click(function(){
        // check if the price has been overrided
         var $this = $(this);
         var registrant_form = $this.closest('.registrant-form');
         var override_node = $(registrant_form).find('.admin-override'),
            override_price_node = $(registrant_form).find('.admin-override_price');

        var override = false;
        var override_checked = $($(override_node).find('input[type=checkbox]:checked')).length > 0;
        var override_price = parseInt($(override_price_node).find('input[type=text]').val());

        if (!override_checked || isNaN(override_checked)){

            var name_attr = $this.attr('name');
             var this_price = $this.next('strong').find('span').data('price');
             //var id_regex = new RegExp('(registrant_(\\d+))');
             var idx = get_idx(name_regexp, name_attr);

             updateSummaryEntry('registrant', idx, this_price);
        }

    });
    {% endif %}

    {% if not event.is_table %}
    // update summary entries
    $('.registrant-form').each(function(){
        $this = $(this);
        var pricing_obj = get_registrant_pricing_obj($this);
        if (pricing_obj !== false ){
            updateSummaryEntry(prefix, pricing_obj.idx, pricing_obj.price);
        }

    });
    {% endif %}

    $('#populate-fields').click(function(e){
        e.preventDefault();
        populate_blank_fields();
    });


    {% if not event.is_table and request.user.is_superuser %}
    var override_checkboxes = $('.admin-override').find('input[type=checkbox]');
    $(override_checkboxes).each(function(){
        var checkbox = this;
        var price_box = $(checkbox).closest('.admin-override').next();
        toggle_admin_override(checkbox, price_box);
    });


    $(override_checkboxes).change(function(){
        var checkbox = this;
        var price_box = $(checkbox).closest('.admin-override').next();
        toggle_admin_override(checkbox, price_box);

        var registrant_form = $(this).closest('.registrant-form');

        override_update_summary_entry(prefix, registrant_form);

    });

    $('.admin-override_price').change(function() {
        var registrant_form = $(this).closest('.registrant-form');

        override_update_summary_entry(prefix, registrant_form);

    });

    {% endif %}


    {% if event.is_table and request.user.is_superuser %}
    // toggle admin override for table
    var override_tbl_checkboxes = $('#admin-override-table').find('input[type=checkbox]');
    var override_price_tbl_box = $('#admin-override-price-table');
    var override_price_tbl_input = $(override_price_tbl_box).find('input[name=override_price_table]');
    toggle_admin_override(override_tbl_checkboxes, override_price_tbl_box);

    $(override_tbl_checkboxes).change(function(){
        toggle_admin_override(override_tbl_checkboxes, override_price_tbl_box);

        var override = false;
        var override_price = 0;
        var should_update = true;
        if ($(this).is(':checked')){
            override_price = parseFloat($(override_price_tbl_input).val());
            if (!isNaN(override_price)){
                override = true;
            }else{
                // cliked but no price entered
                should_update = false;
            }
        }
        if (should_update){
            table_override_update_summary_entry('registrant', override, override_price);
        }

    });

    $(override_price_tbl_input).change(function(){
        if ($(override_tbl_checkboxes).is(':checked')){
            var override_price = parseFloat($(this).val());
            table_override_update_summary_entry('registrant', true, override_price);
        }
    });

    {% endif %}

});