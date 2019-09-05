$(document).ready(function() {
    // for the forms module
    function toogle_tax_rate_field(element) {
        if (element.is(':checked')) {
            element.parent().parent().next().show();
        } else {
            element.parent().parent().next().hide();
        }
    }

    function hook_taxable_fields_js() {
        $(".field-taxable > div > input").each(function() {
            toogle_tax_rate_field($(this));
            $(this).on("click", function() {
                toogle_tax_rate_field($(this));
            });
        });
    }
    hook_taxable_fields_js();

});
