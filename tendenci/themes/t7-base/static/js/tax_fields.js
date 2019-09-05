$(document).ready(function() {
    function toggle_tax_rate_field(element) {
        if (element.is(":checked")) {
            element.parent().parent().next().show();
        } else {
            element.parent().parent().next().hide();
        }
    }
    var include_tax = $("#id_include_tax");
    toggle_tax_rate_field(include_tax);
    include_tax.on("click", function() {
        toggle_tax_rate_field($(this));
    });
});
