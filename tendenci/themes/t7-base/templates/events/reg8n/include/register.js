function generatePreviewElements(){
    var prev_conf = $('#preview-confirmation');
    prev_conf.empty();
    prev_conf.append("<p>Registering the following people:</p>");
    var children = $('#registrant-forms').children('.registrant-form').each(function(index, value){
        var dvalue = $(value);
        var first_name = dvalue.find('#id_registrant-'+(index)+'-first_name').val();
        var last_name = dvalue.find('#id_registrant-'+(index)+'-last_name').val();
        prev_conf.append("<p>"+first_name+" "+last_name+"</p>");
    });

};

$(document).ready(function(){
    $('#discount_check').on("click", function(){
        code = $('#id_discount_code').val();
       // price = $('#total-amount').html();
        //count = 1;
        var model = 'registrationconfiguration';
        var prices = '';
        {% if event.is_table %}
         prices = $('#summary-total-price span#total-amount').html();
        {% else %}
        $('#summary-price span.item-price').each(function(){
            if (prices == ''){
                prices = $(this).html();
            }else{
                prices = prices + ';' +  $(this).html();
            }
        });
        {% endif %}

        $.post(
            '{% url "discount.discounted_prices" %}',
            {
                'code':code,
                'prices':prices,
                'model':model,
            },
            function(data, textStatus, jqXHR){
                json = JSON.parse(data);
                //alert(json['message'])
                $('#discount-message').html(json["message"]);
                if (!json["error"]){
                    $('#summary-total-amount').html(json["total"]);
                    $('#discount-amount').html(json["discount_total"]);
                    $('#final-amount').html(json["total"]);
                    $('.discount-summary').show()
                } else {
                    $('#summary-total-amount').html($('#total-amount').html());
                    $('#discount-amount').html("0.00");
                    $('#final-amount').html($('#total-amount').html());
                }
            }
        );
    });

    $('#registration-form').on("submit", function() {
        $(this).find('#register-button').off('click').on('click', function() {
            return false;
        }).css('opacity', '0.5');
    });
});
