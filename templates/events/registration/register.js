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

function getPricingList(){
    var email = $('#pricing-email').val();
    var memberid = $('#pricing-memberid').val();
    $.ajax({
        url: "{% url event.reg_pricing event.pk %}",
        type: "GET",
        data: {'email':email, 'memberid':memberid},
        dataType: "json",
        success: function(d){
            var p_list = d['pricings'];
            var a_list = d['addons'];
            
            // reinitialize pricings
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
                p_html = p_html + ' ' + p_list[i]['title'] + ' (' + p_list[i]['quantity'] + ' for {{ SITE_GLOBAL_CURRENCYSYMBOL }}' + p_list[i]['price'] + ')</div>'
            }
            $('#pricing-choices').html(p_html);
            
            //reinitialize addons
            var a_html = "";
            for(i=0; i<a_list.length; i++){
                a_html = a_html + '<div '
                if(a_list[i]['enabled']){
                    a_html = a_html + '>'
                } else {
                    a_html = a_html + "class='gray-text'>"
                }
                a_html = a_html + '<input type="radio" name="add-addons" value="' + a_list[i]['pk'] + '"'
                a_html = a_html + 'quantity="'+ a_list[i]['quantity'] +'" price="' + a_list[i]['price'] + '"'
                a_html = a_html + 'title="' + a_list[i]['title'] + '"' + ' is_public="' + a_list[i]['is_public'] + '"'
                if(a_list[i]['enabled']){
                    a_html = a_html + '>'
                }else{
                    a_html = a_html + ' DISABLED>'
                }
                a_html = a_html + ' ' + a_list[i]['title'] + ' ({{ SITE_GLOBAL_CURRENCYSYMBOL }}' + a_list[i]['price'] + ')</div>'
            }
            $('#addon-choices').html(a_html);
        }
    });
};

function updateSummaryEntry(prefix, idx, price){
    // update the summary entry in the summary table
    // insert it into the table if it does not exist yet
    ver = entry_id = '#summary-'+prefix+'-'+idx
    var summary_table = $('#summary-price');
    var entry = $(entry_id);
    if(entry.length>0){
        entry.find('.price').html(price);
    }else{
        var row = $('#summary-item-hidden').clone(true);
        row.attr('id', 'summary-'+prefix+'-'+idx);
        row.find('.item-price').html(price);
        row.find('.item-label').html(prefix + " #" + idx);
        summary_table.append(row);
    }
    updateSummaryTotal();
}

function removeSummaryEntry(prefix, idx){
    var entry = $('#summary-'+prefix+'-'+idx);
    entry.remove();
    updateSummaryTotal();
}

function updateSummaryTotal(){
    // update the total
    var summary_table = $('#summary-price');
    var items = $('#summary-price>tr');
    var total_amount = 0;
    for(i=0;i<items.length;i++){
        item_amount = parseFloat($(items[i]).find('.item-price').html());
        total_amount = total_amount + item_amount;
    }
    $('#total-amount').html(total_amount.toFixed(2));
    $('#final-amount').html(total_amount.toFixed(2));
}

$(document).ready(function(){
    // REGISTRANT CONTROLS
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
                updateSummary(this_form, 'registrant', i);
            }
        }
        return false;   // cancel
    });
    
    $('.first-registrant-email').blur(function(){
        form = $(this).parent().parent().parent()
        getUserStatus(form);
    });

    $('.first-registrant-memberid').blur(function(){
        form = $(this).parent().parent().parent()
        getUserStatus(form);
    });
    
    $('.registrant-header').click(function() {
        $(this).parent().children('div:last').toggle();
        if ($(this).children('span.showhide').text() == "+ ") {
            $(this).children('span.showhide').text('- ');
        } else 
        {$(this).children('span.showhide').text('+ '); }
    });
    
    //MISC CONTROLS
    $('#pricing-check').click(function(){
        getPricingList();
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

});
