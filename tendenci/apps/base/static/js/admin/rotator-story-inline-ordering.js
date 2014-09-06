position_field = 'rotator_position';

jQuery(function($) {
    // This script is applied to all TABULAR inlines
    $('div.inline-group div.tabular').each(function() {
        table = $(this).find('table');

        // Drag and drop functionality - only used if a position field exists
        if (position_field !== '' && table.find('td').is('.field-' + position_field))
        {
            // Hide "position"-field (both td:s and th:s)
            // $(this).find('td.field-' + position_field).hide();
            //td_pos_field_index = table.find('tbody tr td').index($(this).find('td.field-' + position_field));
            //$(this).find('th:eq(' + (td_pos_field_index-1) + ')').hide();
            var pos_td = $(this).find('td.field-' + position_field);
            var input = $(pos_td).children('input');
            input.hide();
            var label = $('<span><img src="/static/images/icons/drag_icon_16x16.png" alt="drag icon 16x16" title="drag icon 16x16" /></span>');
            $(pos_td).append(label);

            // Make table sortable using jQuery UI Sortable
            table.sortable({
                items: 'tr:has(td)',
                tolerance: 'pointer',
                axis: 'y',
                cancel: 'input,button,select,a',
                helper: 'clone',
                update: function() {
                    update_positions($(this), true);
                }
            });

            // Re-order <tr>:s based on the "position"-field values.
            // This is a very simple ordering which only works with correct position number sequences,
            // which the rest of this script (hopefully) guarantees.
            rows = [];
            table.find('tbody tr:not(.empty-form):not(.add-row)').each(function() {
                position = $(this).find('td.field-' + position_field + ' input').val();
                rows[position] = $(this);

                // Add move cursor to table row.
                table.find('tr:has(td)').css('cursor', 'move');
            });
            empty_field = table.find('tbody tr.empty-form');
            add_field = table.find('tbody tr.add-row');

            for (var i in rows) { table.append(rows[i]); } // Move <tr> to its correct position
            table.append(empty_field);
            table.append(add_field);
            update_positions($(this));
        }
        else {
            position_field = '';
        }
    });
});

// Updates "position"-field values based on row order in table
function update_positions(table, update_position)
{
    even = true;
    num_rows = 0;
    position = 0;

    // Set correct position: Filter through all trs, excluding first th tr and last hidden template tr
    table.find('tbody tr:not(.add_template):not(.deleted_row)').each(function() {
        if (position_field !== '') {

            input = $(this).find('td.field-' + position_field + ' input');

            var attr_id = input.attr('id');

            var is_prefix = -1;
            if(attr_id){
                is_prefix = attr_id.indexOf('__prefix__');
            }

            if(is_prefix < 0){

                if(update_position){
                    input.val(position+1);
                    position++;
                }

                // Update row coloring
                $(this).removeClass('row1 row2');
                if (even)
                {
                    $(this).addClass('row1');
                    even = false;
                }
                else
                {
                    $(this).addClass('row2');
                    even = true;
                }
            }
        }
    });
}
