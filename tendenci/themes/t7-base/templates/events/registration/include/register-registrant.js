var validate_guest = false;
{% if custom_reg_form.validate_guest %}
    validate_guest = true;
{% endif %}

//delete registrant js
function deleteRegistrant(ele, prefix) {
    var registrant_form = $(ele);
    var attr_id = $(registrant_form).attr("id");
    // remove the registrant form
    $(registrant_form).remove();
    // update the TOTAL_FORMS
    var forms = $(".registrant-form");
    $("#id_" + prefix + "-TOTAL_FORMS").val(forms.length);
    // remove the reg price entry
    var reg_id = attr_id.split('_')[1];
    removeSummaryEntry(prefix, reg_id);
}


//formset index update
function updateIndex(e, prefix, idx){
    var id_regex = new RegExp('(registrant-\\d+)');
    var replacement = prefix + '-' + idx
    if ($(e).attr("for"))
        {$(e).attr("for", $(e).attr("for").replace(id_regex, replacement));}
    if (e.id) {e.id = e.id.replace(id_regex, replacement);}
    if (e.name){e.name = e.name.replace(id_regex, replacement);}
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
        if (validate_guest == false){
            // remove required att
            $(row).find('div.label').removeClass("required");
       }
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
    delete_button.prop('id', false );
    container.append(delete_button);
    $('#registrant-forms').append(container);
    return false;
}

$(document).ready(function(){
    // REGISTRANT CONTROLS
    default_pricings = $('#pricing-choices').html();
    // add registrant set button
    $("#add-registrants-button").on("click", function(){
        var pricing = $('input:radio[name=add-registrants-pricing]:checked');
        var price_d = {};
        if(pricing.val()){
            reg_num = parseInt($("#add-registrants-number").val());
            price_d['quantity'] = pricing.attr('quantity');
            price_d['price'] = pricing.attr('price');
            price_d['title'] = pricing.attr('title');
            price_d['pk'] = pricing.val();
            price_d['is_public'] = pricing.attr('is_public');
            {% if not shared_pricing %}
                if((reg_num > 1)&&(!(price_d['is_public'].toString().toLowerCase()=='true'))){
                    alert('You cannot add multiple registrants for non public pricings.');
                    return false;
                }
            {% endif %}
            var init_d = {};
            var blank_d = {};
            init_d['email'] = $('#pricing-email').val();
            blank_d['email'] = '';
            $('#pricing-email').val('');
            init_d['memberid'] = $('#pricing-memberid').val();
            blank_d['memberid'] = '';
            $('#pricing-memberid').val('');
            for(var i=0; i<reg_num; i++){
                if(i==0){//only the first set will have email and memberid data
                    addRegistrantSet('registrant', price_d, init_d);
                }else{
                    addRegistrantSet('registrant', price_d, blank_d);
                }
            }
            {% if not shared_pricing %}
                $('#pricing-choices').html(default_pricings);
                $('#add-registrants-number').val(1);
            {% endif %}
        } else {
            alert("Please select a pricing first.");
        }
    });

    // show delete-button-wrap
    $(".delete-button-wrap").show();
    // delete registrant set button
    $('.delete-button').live('click', function(){
        var delete_confirm = confirm('Are you sure you want to delete this registrant set?');   // confirm
        if(delete_confirm) {
            // delete each form in the set
            var set = $($($($(this).parent()).parent()).parent());
            var forms = set.find('.registrant-form');
            for(i=0;i<forms.length;i++){
                deleteRegistrant(forms[i], 'registrant');
            }
            set.remove();

            // update form index
            forms = $('.registrant-form');
            var this_form;
            for (var i=0, formCount=forms.length; i<formCount; i++){
                this_form = forms.get(i);
                $(this_form).find(".form-field").children().children().each(function() {
                    if (this){
                        updateIndex(this, 'registrant', i);
                    }
                });
                updateFormHeader(this_form, 'registrant', i, 0);
            }
        }
        return false;   // cancel
    });

    $('.first-registrant-email').on("blur", function(){
        form = $(this).parent().parent().parent()
        getUserStatus(form);
    });

    $('.first-registrant-memberid').on("blur", function(){
        form = $(this).parent().parent().parent()
        getUserStatus(form);
    });

    $('.registrant-header').on("click", function() {
        $(this).parent().children('div:last').toggle();
        if ($(this).children('span.showhide').text() == "+ ") {
            $(this).children('span.showhide').text('- ');
        } else
        {$(this).children('span.showhide').text('+ '); }
    });
});
