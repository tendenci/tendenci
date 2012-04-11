$(document).ready(function(){
    $('#discount_check').click(function(){
        code = $('#id_discount_code').val();
        price = $('#total-amount').html();
        // only 1 registrant set is discounted
        count = 1;
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
});
