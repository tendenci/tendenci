var price_quantity = {{ price.quantity }};
var price_price = {{ price.price }}

function deleteRegistrant(ele, prefix) {
    var registrant_form = $(ele).parents('.registrant-form');
    var attr_id = $(registrant_form).attr("id");
    
    // remove the registrant form
    $(registrant_form).remove();
    
    // update the TOTAL_FORMS
    var forms = $(".registrant-form");
    $("#id_" + prefix + "-TOTAL_FORMS").val(forms.length);
    
    // update the total amount and remove the reg price entry
    var reg_id = attr_id.split('_')[1];
    var reg_id_0 = reg_id-1
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
        $(reg_header).parent().children('div:last').hide();
        $(reg_header).children('span.showhide').text('+ ');
        var ic = $(reg_header).find('.item-counter');
        if (ic) {
            $(ic).html(idx);}
    };
    
}

function addRegistrant(ele, prefix, price) {
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('.registrant-form:first').clone(true).get(0);
    $('.registrant-form:first').find('.registrant-header').removeClass('hidden');
    $(row).insertAfter($('.registrant-form:last')).find('.hidden').removeClass('hidden');
    // remove the error
    $(row).find('div.error').remove();
    {% if not custom_reg_form.validate_guest %}
    // remove required att
    $(row).find('div.label').removeClass("required");
    {% endif %}
    // update id attr
    var id_regex = new RegExp('(registrant_\\d+)');
    var replacement = prefix + '_' + formCount;
    if(row.id){
        row.id = row.id.replace(id_regex, replacement);
    }
    $(row).find(".form-field").children().children().each(function() {
        updateIndex(this, prefix, formCount);
        $(this).val('');
    });
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    updateFormHeader(row, prefix, formCount);
    updateSummaryEntry(prefix, formCount, price);
    return false;
}

function add_registrants(e, prefix) {
    extra_count = $(e).parent().find('.extra-registrants').val();
    extra_count = parseInt(extra_count);
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

$(document).ready(function(){
    // show delete-button-wrap
    $(".delete-button-wrap").show();
    // delete confirmation
    $('button.delete-button').live('click', function(){
        var delete_confirm = confirm('Are you sure you want to delete this registrant?');   // confirm
        if(delete_confirm) {
            return deleteRegistrant(this, 'registrant');
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
});
