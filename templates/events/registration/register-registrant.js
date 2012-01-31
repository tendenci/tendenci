//delete registrant js
function deleteRegistrant(ele, prefix) {
    var registrant_form = $(ele);
    var attr_id = $(registrant_form).attr("id");
    
    // remove the registrant form
    $(registrant_form).remove();
    
    // update the TOTAL_FORMS
    var forms = $(".registrant-form");
    $("#id_" + prefix + "-TOTAL_FORMS").val(forms.length);
    
    // update the total amount and remove the reg price entry
    var reg_id = attr_id.split('_')[1];
    var registrant_summary_entry = $("tr[id=summary-item_" + reg_id + "]");
    var registrant_price = $(registrant_summary_entry).find(".reg-price").html();
    
    removeSummaryEntry(prefix, reg_id);
}


//formset index update
function updateIndex(e, prefix, idx){
    var id_regex = new RegExp('(registrant-\\d+)');
    var replacement = prefix + '-' + idx
    if ($(e).attr("for")) 
        {$(e).attr("for", $(e).attr("for").replace(id_regex, replacement));}
    if (e.id) {e.id = e.id.replace(id_regex, replacement);}
    if (e.name){ e.name = e.name.replace(id_regex, replacement);}
}

// update the serial number on the form. ex: Registrant #3, Reg #3
function updateFormHeader(this_form, prefix, idx, hide_form){
    // change the serial number on the form
    var id_regex = new RegExp('(registrant_\\d+)');
    var replacement = prefix + '_' + idx
    if (this_form.id) {this_form.id = this_form.id.replace(id_regex, replacement);}

    var reg_header = $(this_form).find('.registrant-header');
    if (reg_header) {
        if(hide_form==1){
            $(reg_header).parent().children('div:last').hide();
        }else if(hide_form==-1){
            $(reg_header).parent().children('div:last').show();
        }
        $(reg_header).children('span.showhide').text('+ ');
        var ic = $(reg_header).find('.item-counter');
        if (ic) {
            $(ic).html(idx+1);
        }
    };
    
}

function addRegistrant(prefix, pricing, initial_data, set_container, hide_form){
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('#registrant-hidden').clone(true).get(0);
    // place proper class
    $(row).addClass('registrant-form');
    if(formCount > 0){
        // remove required att
        $(row).find('div.label').removeClass("required");
    };
    
    // update id attr
    var replacement = prefix + '_' + formCount
    $(row).attr('id',replacement);
    
    $(row).find(".form-field").children().children().each(function() {
        updateIndex(this, prefix, formCount);
        if($(this).attr("name")==(prefix+"-"+formCount+"-pricing")){
            // assign pricing selected
            $(this).val(pricing['pk'])
        }else if($(this).attr("name")==(prefix+"-"+formCount+"-email")){
            // assign email selected
            if(initial_data['email']){
                $(this).val(initial_data['email'])
            }else{
                // default if no email and 1st form
                if(formCount>0){
                    $(this).val(initial_data['email'])
                }
            }
        }else if($(this).attr("name")==(prefix+"-"+formCount+"-memberid")){
            // assign memberid selected
            $(this).val(initial_data['memberid'])
        }else{
            // clear the field
            if(formCount > 0){
                $(this).val("")
            }
        }
    });
    
    // insert as last element into form list
    $(set_container).append(row);
    
    updateFormHeader(row, prefix, formCount, hide_form);
    
    updateSummaryEntry(prefix, formCount, pricing['price']);
    
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    
    // attempt to get the user status for this form
    if(hide_form==-1){
        $(row).find('.registrant-email').attr('class', 'registrant-email first-registrant-email')
        $(row).find('.registrant-memberid').attr('class', 'registrant-memberid first-registrant-memberid')
        getUserStatus(row);
    }else{
        
    }
    
    return false;
}

function addRegistrantSet(prefix, pricing_data, initial_data){
    var pricing = $.extend(pricing_data);
    extra_count = pricing['quantity'];
    container = $('<div class="registrant-set"></div>');
    container.append("<h2>"+pricing['title']+"</h2>");
    if (extra_count > 0){
        //only the first one is charged in a set
        //only the first one has initial data
        addRegistrant(prefix, pricing, initial_data, container, -1);
        //the rest will have 0 price
        for (var i=1; i<extra_count; i++) {
            pricing['price'] = 0.00;
            addRegistrant(prefix, pricing, {}, container, 1);
        }
    }
    delete_button = $("#delete-hidden").clone(true);
    delete_button.removeAttr('id');
    container.append(delete_button);
    $('#registrant-forms').append(container);
    return false;
}
