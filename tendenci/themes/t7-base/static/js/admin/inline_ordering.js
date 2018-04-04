// sort tabular inline fields
jQuery(function($) {
	
        $('div.inline-group').sortable({
            items: 'tr.dynamic-cma_fields',
            handle: 'td',
            update: function() {
                $(this).find('tr.dynamic-cma_fields').each(function(i) {
                    $(this).find('input[name$=order]').val(i+1);
                    $(this).removeClass('row1').removeClass('row2');
                    $(this).addClass('row'+((i%2)+1));
                });
            }
        });

        $('.inline-related tbody').css('cursor', 'move');
        $('.inline-related .add-row').css('cursor', 'default');
    });
