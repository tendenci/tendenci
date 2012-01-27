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
