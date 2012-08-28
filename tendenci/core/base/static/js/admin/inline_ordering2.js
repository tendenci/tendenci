// sort stacked inline fields for corpapp
jQuery(function($) {
    $('div.inline-group').sortable({
        containment: 'parent',
        items: 'div.inline-related',
        handle: 'h3:first'
//        update: function() {
//            $(this).find('div.inline-related').not('div.inline-related:last').each(function(i) {
//                //if ($(this).find('input[id$=label]').val()) {
//                    $(this).find('input[id$=order]').val(i+1);
//                //}
//            });
//        }
    });
    $('div.inline-related h3').css('cursor', 'move');
    $('div.inline-related').find('input[id$=order]').parent('div').hide();
    
    $('#corpapp_form').submit(function() {
        $('div.inline-group > div.inline-related').not('div.inline-related:last').each(function(i) {
            //if ($(this).find('input[id$=label]').val()) {
                $(this).find('input[id$=order]').val(i+1);
            //}
        });
    });

    
});