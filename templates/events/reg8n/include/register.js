$(document).ready(function(){
    $('#discount_check').click(function(){
        code = $('#id_discount_code').val();
        price = $('#original-price').html();
        count = parseInt($('#id_registrant-TOTAL_FORMS').val());
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
});
