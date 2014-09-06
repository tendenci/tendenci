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
            $('.add-addons-box').html(d['add-addons-form']);
        }
    });
};

$(document).ready(function(){
    //MISC CONTROLS
    $('#pricing-check').click(function(){
        getPricingList();
    });

    $('#discount_check').click(function(){
        var code = $('#id_discount').val();
        var price = $('#total-amount').html();
        var count = 1;
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
                    $('#summary-total-amount').html($('#total-amount').html());
                    $('#discount-amount').html("0.00");
                    $('#final-amount').html($('#total-amount').html());
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
