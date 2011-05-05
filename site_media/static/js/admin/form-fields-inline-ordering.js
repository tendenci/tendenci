// sort tabular inline fields
jQuery(function($) {
	// This reodering screws with the exports. Might try to find a way to update the db _order column without doing it this way.
	/*
        $('div.inline-group').sortable({
            items: 'tr.dynamic-fields',
            handle: 'td',
            update: function() {
                $(this).find('tr.dynamic-fields').each(function(i) {
                    $(this).removeClass('row1').removeClass('row2');
                    $(this).addClass('row'+((i%2)+1));
                    $(this).attr('id','fields-'+i);
                    var j=i;
                    $(this).find('td').each(function(i) {
                        if ($(this).attr('class') == 'original') {

                            $(this).find('input[id$=-id]').attr('id','id_fields-'+j+'-id');
                            $(this).find('input[id$=-form]').attr('id','id_fields-'+j+'-form');
                            $(this).find('input[id$=-id]').attr('value',j+1);
                             }
                        else {
                            $(this).find('input').attr('id','id_fields-'+j+'-'+$(this).attr('class'));
                            $(this).find('select').attr('id','id_fields-'+j+'-'+$(this).attr('class'));
                        }      
                    });
                });
            }
        });
        
        $('.inline-related tbody').css('cursor', 'move');
        $('.inline-related .add-row').css('cursor', 'default');
        */
    });
