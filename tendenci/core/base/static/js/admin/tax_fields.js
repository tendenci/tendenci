$(document).ready(function() {
    // for the forms module
    function hide_show_rate1(element) {
        if (element.is(':checked')) {
            element.parent().parent().next().show();
        } else {
            element.parent().parent().next().hide();
        }
    }

    function hook_taxable_fields_js() {
        $(".field-taxable > div > input").each(function() {
            hide_show_rate1($(this));
            $(this).click(function() {
                hide_show_rate1($(this));
            });
        });
    }
    hook_taxable_fields_js();

});