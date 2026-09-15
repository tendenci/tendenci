(function($) {
	var form = document.getElementById('payment-form');
	if (!form) {
		return;
	}

	var clientSecret = form.getAttribute('data-client-secret');
	var finalizeUrl = form.getAttribute('data-finalize-url');
	var saveBillingUrl = form.getAttribute('data-save-billing-url');
	var errorElement = document.getElementById('payment-errors');

	if (!clientSecret || typeof stripe === 'undefined') {
		if (errorElement) {
			errorElement.textContent = 'Payment form is not ready. Please refresh the page.';
		}
		return;
	}

	var elements = stripe.elements({ clientSecret: clientSecret });
	var paymentElement = elements.create('payment');
	paymentElement.mount('#payment-element');

	paymentElement.on('change', function(event) {
		if (event.error) {
			errorElement.textContent = event.error.message;
		} else {
			errorElement.textContent = '';
		}
	});

	function getCsrfToken() {
		var input = form.querySelector('input[name=csrfmiddlewaretoken]');
		return input ? input.value : '';
	}

	function validateFields() {
		var zip = form.querySelector('input[name=zip]');
		var zipVal = zip ? zip.value : '';
		if (zipVal === '') {
			if (zip) {
				$(zip).siblings('.error').html('Zip Code is a required field');
			}
			return false;
		}
		return true;
	}

	function saveBilling() {
		var formData = new FormData(form);
		return fetch(saveBillingUrl, {
			method: 'POST',
			headers: {
				'X-CSRFToken': getCsrfToken()
			},
			body: formData,
			credentials: 'same-origin'
		}).then(function(response) {
			return response.json().then(function(data) {
				if (!response.ok || !data.ok) {
					var message = 'Unable to save billing information.';
					if (data && data.errors) {
						var parts = [];
						Object.keys(data.errors).forEach(function(key) {
							parts = parts.concat(data.errors[key]);
						});
						if (parts.length) {
							message = parts.join(' ');
						}
					} else if (data && data.error) {
						message = data.error;
					}
					throw new Error(message);
				}
				return data;
			});
		});
	}

	function resetSubmit() {
		$('.submit-button').prop('disabled', false);
		$('#submit-loader').hide();
	}

	form.addEventListener('submit', function(e) {
		e.preventDefault();
		if (!validateFields()) {
			return;
		}

		$('.submit-button').attr('disabled', 'disabled');
		$('#submit-loader').show();
		errorElement.textContent = '';

		saveBilling().then(function() {
			return stripe.confirmPayment({
				elements: elements,
				confirmParams: {
					return_url: finalizeUrl
				},
				redirect: 'if_required'
			});
		}).then(function(result) {
			if (result.error) {
				errorElement.textContent = result.error.message;
				resetSubmit();
				return;
			}
			if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
				var sep = finalizeUrl.indexOf('?') === -1 ? '?' : '&';
				window.location = finalizeUrl + sep + 'payment_intent=' + encodeURIComponent(result.paymentIntent.id);
				return;
			}
			// Redirect-based methods are handled by return_url
		}).catch(function(err) {
			errorElement.textContent = err.message || String(err);
			resetSubmit();
		});
	});
}(jQuery));
