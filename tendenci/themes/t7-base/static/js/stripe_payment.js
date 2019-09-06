(function($) {
	
	var elements = stripe.elements();
	var card = elements.create('card', {
		  hidePostalCode: true,
		  style: {
		    base: {
		      iconColor: '#F99A52',
		      color: '#32315E',
		      lineHeight: '48px',
		      fontWeight: 400,
		      fontFamily: '"Helvetica Neue", "Helvetica", sans-serif',
		      fontSize: '15px',

		      '::placeholder': {
		        color: '#CFD7DF',
		      }
		    },
		  }
		});
	card.mount('#card-element');
	
	card.on('change', function(event) {
		  var displayError = document.getElementById('card-errors');
		  if (event.error) {
		    displayError.textContent = event.error.message;
		  } else {
		    displayError.textContent = '';
		  }
	});
	
	function stripeTokenHandler(token) {
		  // Insert the token ID into the form so it gets submitted to the server
		  var form = document.getElementById('payment-form');
		  var hiddenInput = document.createElement('input');
		  hiddenInput.setAttribute('type', 'hidden');
		  hiddenInput.setAttribute('name', 'stripe_token');
		  hiddenInput.setAttribute('value', token.id);
		  form.appendChild(hiddenInput);
	
		  // Submit the form
		  form.submit();
	}

	function createToken() {
			var extraDetails = {
				    name: form.querySelector('input[id=id_card_name]').value,
				    address_line1: form.querySelector('input[name=address]').value,
				    address_line2: form.querySelector('input[name=address2]').value,
				    address_city: form.querySelector('input[name=city]').value,
				    address_state: form.querySelector('input[name=state]').value,
				    address_zip: form.querySelector('input[name=zip]').value,
				    address_country: form.querySelector('input[name=country]').value,
				    email: form.querySelector('input[name=email]').value,
				    company: form.querySelector('input[name=company]').value,
				    phone: form.querySelector('input[name=phone]').value
				    
		    };
		    stripe.createToken(card, extraDetails).then(function(result) {
		      if (result.error) {
		        // Inform the user if there was an error
		        var errorElement = document.getElementById('card-errors');
		        errorElement.textContent = result.error.message;
		        $('.submit-button').prop('disabled', false );
		        $('#submit-loader').hide();
		      } else {
		       // Send the token to your server
		        stripeTokenHandler(result.token);
		      }
		  });
	};
	
	function validateFields() {
		var name = form.querySelector('input[id=id_card_name]').value;
		var zip = form.querySelector('input[name=zip]').value;
		
		if (name == "" | zip == ""){
			if (name == ""){
				$('#id_card_name').next('.error').html("Name on Card is a required field");
			}
			if (zip == ""){
				$('#id_zip').next('.error').html("Zip Code is a required field");
			}
			return false;
		}else{
			return true;
		}
	};

	// Create a token when the form is submitted.
	var form = document.getElementById('payment-form');
	form.addEventListener('submit', function(e) {
		  e.preventDefault();
		  if (validateFields()){
			  $('.submit-button').attr("disabled", "disabled");
			  $('#submit-loader').show();
			  createToken();
		  }
	});
	
}(jQuery));
