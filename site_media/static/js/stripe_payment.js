function stripeResponseHandler(status, response) {
    if (response.error) {
       
        //show the errors on the form
        $("#card-errors").addClass('errors');
        $("#card-errors").html(response.error.message);
        $('.submit-button').removeAttr('disabled');
        $('#submit-loader').hide();
        
    } else {
        var form$ = $("#payment-form");
        // token contains id, last4, and card type
        var token = response['id'];
        // insert the token into the form so it gets submitted to the server
        form$.append("<input type='hidden' name='stripe_token' value='" + token + "'/>");
        // and submit
        form$.get(0).submit();
    }
}

function PopupLink(oLink) {
	if (null != oLink) { 
 		window.open(oLink.href, null, "height=350, width=450, scrollbars=1, resizable=1");
		return false;
	}
	return true;
}

$(document).ready(function() {
  $("#payment-form").submit(function(event) {
    // disable the submit button to prevent repeated clicks
    $('.submit-button').attr("disabled", "disabled");
    $('#submit-loader').show();

    Stripe.createToken({
        number: $('.card-number').val(),
        cvc: $('.card-cvc').val(),
        exp_month: $('.card-expiry-month').val(),
        exp_year: $('.card-expiry-year').val()
    }, stripeResponseHandler);

    // prevent the form from submitting with the default action
    return false;
  });
});


	
	
