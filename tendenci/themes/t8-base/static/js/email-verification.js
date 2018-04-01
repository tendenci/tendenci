$('.email-verification-0').each(function() {
    // Save current value of element
    $(this).data('oldVal', $(this).val());
    // Look for changes in the value
    $(this).bind("blur", function(event){
        // If value has changed...
        if ($(this).data('oldVal') != $(this).val() && $(this).val() !='') {
            // Updated stored value
            $(this).data('oldVal', $(this).val());
            var otherval = $(this).parent().children('.email-verification-1').val();
            if(($(this).val() != otherval) && (otherval !='') && (otherval != 'Confirm Email')) {
                $(this).parent().children('.email-verfication-error').show();
            }else {
                $(this).parent().children('.email-verfication-error').hide();
            }

            if ($(this).val() === '' || $(this).val() === 'Email')
                $(this).parent().children('.email-verfication-error').hide();
        }
    });
});

$('.email-verification-1').each(function() {
    // Save current value of element
    $(this).data('oldVal', $(this).val());
    // Look for changes in the value
    $(this).bind("blur", function(event){
        // If value has changed...
        if ($(this).data('oldVal') != $(this).val()) {
            // Updated stored value
            $(this).data('oldVal', $(this).val());
            var otherval = $(this).parent().children('.email-verification-0').val();
            if(($(this).val() != otherval) && (otherval !='') && (otherval != 'Email')) {
                $(this).parent().children('.email-verfication-error').show();
            }else {
                $(this).parent().children('.email-verfication-error').hide();
            }

            if ($(this).val() === '' || $(this).val() === 'Confirm Email')
                $(this).parent().children('.email-verfication-error').hide();
        }
    });
});
