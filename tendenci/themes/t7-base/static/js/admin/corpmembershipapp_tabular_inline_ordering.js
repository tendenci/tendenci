jQuery(function($) {
    $("div.inline-group").sortable({
        axis: 'y',
        placeholder: 'ui-state-highlight',
        forcePlaceholderSize: 'true',
        items: '.row1, .row2',
        update: update
    });
    //$("div.inline-group").disableSelection();
});
function update() {
    $('.row1, .row2').each(function(i) {
        $(this).find('input[id$=position]').val(i+1);
    });
}
jQuery(document).ready(function($){
    // hide order
    var order_index = $('div.inline-related').find('td.field-position').index();
    $('div.inline-related').find('td.field-position').hide();
    $('div.inline-related').find('th:nth-child(' + order_index +')').hide();

    //$('div.inline-related tr').css('cursor','move');

    $('.add-row a').click(update);

    $('#corpmembershipapp_form').on("submit", function() {
        update();
    });
});
