$('.email-verification-0').each(function() {
    // Save current value of element
    $(this).data('oldVal', $(this).val());
    // Look for changes in the value
    $(this).bind("propertychange keyup input paste", function(event){
        // If value has changed...
        if ($(this).data('oldVal') != $(this).val()) {
            // Updated stored value
            $(this).data('oldVal', $(this).val());
            if($(this).val() != $(this).parent().children('.email-verification-1').val()) {
                $(this).parent().children('.email-verfication-error').show();
            }else {
                $(this).parent().children('.email-verfication-error').hide();
            }
        }
    });
});

$('.email-verification-1').each(function() {
    // Save current value of element
    $(this).data('oldVal', $(this).val());
    // Look for changes in the value
    $(this).bind("propertychange keyup input paste", function(event){
        // If value has changed...
        if ($(this).data('oldVal') != $(this).val()) {
            // Updated stored value
            $(this).data('oldVal', $(this).val());
            if($(this).val() != $(this).parent().children('.email-verification-0').val()) {
                $(this).parent().children('.email-verfication-error').show();
            }else {
                $(this).parent().children('.email-verfication-error').hide();
            }
        }
    });
});
