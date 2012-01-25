{% load i18n %}

// user status check
function getUserStatus(form){
    var form = $(form)
    var email = form.find('.registrant-email').val();
    var memberid = form.find('.registrant-memberid').val();
    var pricingid = form.find('.registrant-pricing').val();
    
    $.ajax({
        url: "{% url event.reg_user_status event.pk %}",
        type: "GET",
        data: {'email':email, 'memberid':memberid, 'pricingid':pricingid},
        dataType: "json",
        success: function(data){
            if(data){
                var notice= $(form.parent().find('.registrant-notice')[0])
                if(data['error']=='INVALID'){
                    var msg = "<div class='error'>Invalid user for pricing.</div>"
                    notice.html(msg);
                }else if(data['error']=='REG'){
                    var msg = "<div class='error'>User already registered.</div>"
                    notice.html(msg);
                }else if(data['error']=='SHARED'){
                    var msg = "<div class='notice'>Access to this pricing is shared.</div>"
                    notice.html(msg);
                }else{
                    var msg = "<div class='notice'>User already registered but can still register more people.</div>"
                    notice.html(msg);
                }
            }
        }
    });
}

$('.first-registrant-email').blur(function(){
    form = $(this).parent().parent().parent()
    getUserStatus(form);
});

$('.first-registrant-memberid').blur(function(){
    form = $(this).parent().parent().parent()
    getUserStatus(form);
});


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
    var registrant_summary_entry = $("tr[id=price_registrant_" + reg_id + "]");
    var registrant_price = $(registrant_summary_entry).find(".reg-price").html();
    
    var total_amount = $("#total-amount").html();
    total_amount = (parseFloat(total_amount) - parseFloat(registrant_price)).toFixed(2);
    
    $(registrant_summary_entry).remove();
    
    $("#total-amount").html(total_amount);
    $("span.summary-total-amount").html(total_amount);
    $("#original-price").html(total_amount);
    $('#discount-amount').html(0);
    $('#final-amount').html(total_amount);
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

function updateSummary(this_form, prefix, idx){
    // change the serial number in the summary
    var price_item = $('#summary-price').find('tr')[idx];
    if (price_item){
        if (price_item.id){
            price_item.id = 'price_registrant_' + idx;
            var item_counter = $(price_item).find('.item-counter');
            if (item_counter) {$(item_counter).html(idx+1);}
        }
    }   
}

function addSummaryEntry(this_form, prefix, idx, price){
    var row = $('#price_registrant-hidden').clone(true);
    $(row).attr('style', '');
    $(row).find('.item-counter').html(idx+1);
    $(row).find('.reg-price').html(price);
    
    var replacement = 'price_registrant_' + idx;
    $(row).attr('id', replacement);
    
    // append entry to summary box
    $('#summary-price').append(row);
    
    // update the total
    var total_amount = $("#total-amount").html();
    total_amount = (parseFloat(total_amount) + parseFloat($(row).find(".reg-price").html())).toFixed(2);
    $("#total-amount").html(total_amount);
    $("span.summary-total-amount").html(total_amount);
    $("#original-price").html(total_amount);
    $('#discount-amount').html(0);
    $('#final-amount').html(total_amount);
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
    
    addSummaryEntry(row, prefix, formCount, pricing['price']);
    
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

function addRegistrantSet(prefix, pricing, initial_data){
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


$(document).ready(function(){
    default_pricings = $('#pricing-choices').html();
    // add registrant set button
    $("#add-registrants-button").click(function(){
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
            init_d['email'] = $('#pricing-email').val();
            $('#pricing-email').val('');
            init_d['memberid'] = $('#pricing-memberid').val();
            $('#pricing-memberid').val('');
            for(var i=0; i<reg_num; i++){
                addRegistrantSet('registrant', price_d, init_d);
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
                updateSummary(this_form, 'registrant', i);
            }
        }
        return false;   // cancel
    });
});

$('#discount_check').click(function(){
    var code = $('#id_discount_code').val();
    var price = $('#original-price').html();
    var count = parseInt($('#id_registrant-TOTAL_FORMS').val());
    $.post(
        '{% url discount.discounted_price %}',
        {
            'code':code,
            'price':price,
            'count':count,
        },
        function(data, textStatus, jqXHR){
            json = $.parseJSON(data);
            //alert(json['message'])
            $('#discount-message').html(json["message"]);
            if (!json["error"]){
                $('#summary-total-amount').html(json["price"]);
                $('#discount-amount').html(json["discount"]);
                $('#final-amount').html(json["price"]);
                $('.discount-summary').show()
            } else {
                $('#summary-total-amount').html($('#original-price').html());
                $('#discount-amount').html(0);
                $('#final-amount').html($('#original-price').html());
            }
        }
    );
});

$('.registrant-header').click(function() {
    $(this).parent().children('div:last').toggle();
    if ($(this).children('span.showhide').text() == "+ ") {
        $(this).children('span.showhide').text('- ');
    } else 
    {$(this).children('span.showhide').text('+ '); }
});

$('#pricing-check').click(function(){
    getPricingList();
});

function getPricingList(){
    var email = $('#pricing-email').val();
    var memberid = $('#pricing-memberid').val();
    $.ajax({
        url: "{% url event.reg_pricing event.pk %}",
        type: "GET",
        data: {'email':email, 'memberid':memberid},
        dataType: "json",
        success: function(p_list){
            var p_html = "";
            for(i=0; i<p_list.length; i++){
                p_html = p_html + '<div '
                if(p_list[i]['enabled']){
                    p_html = p_html + '>'
                } else {
                    p_html = p_html + "class='gray-text'>"
                }
                p_html = p_html + '<input type="radio" name="add-registrants-pricing" value="' + p_list[i]['pk'] + '"'
                p_html = p_html + 'quantity="'+ p_list[i]['quantity'] +'" price="' + p_list[i]['price'] + '"'
                p_html = p_html + 'title="' + p_list[i]['title'] + '"' + ' is_public="' + p_list[i]['is_public'] + '"'
                if(p_list[i]['enabled']){
                    p_html = p_html + '>'
                }else{
                    p_html = p_html + ' DISABLED>'
                }
                p_html = p_html + p_list[i]['title'] + ' (' + p_list[i]['quantity'] + ' for {{ SITE_GLOBAL_CURRENCYSYMBOL }}' + p_list[i]['price'] + ')</div>'
            }
            $('#pricing-choices').html(p_html);
        }
    });
};

$('.register-submit').click(function(){
    // validate that emails/memberids are only used once.
    
    emails = $('.registrant-email');
    memberids = $('.registrant-memberid');
    
    // check email uniqueness
    var match_found = false;
    for(i=0;i<emails.length-1;i++){
        if($(emails[i]).val()){
            for(j=i+1;j<emails.length-1;j++){
                if($(emails[j]).val()){
                    if($(emails[i]).val() == $(emails[j]).val()){
                        match_found = true
                        break
                    }
                }
            }
            if(match_found){
                break
            }
        }
    };        
    if(match_found){
        alert('{% trans "An email can only be used once per registration!" %}');
        return false;
    }
    
    // check memberid uniqueness
    var match_found = false;
    for(i=0;i<memberids.length-1;i++){
        if($(memberids[i]).val()){
            for(j=i+1;j<memberids.length-1;j++){
                if($(memberids[j]).val()){
                    if($(memberids[i]).val() == $(memberids[j]).val()){
                        match_found = true
                        break
                    }
                }
            }
            if(match_found){
                break
            }
        }
    };        
    if(match_found){
        alert('{% trans "An Member ID can only be used once per registration!" %}');
        return false;
    }        
});
