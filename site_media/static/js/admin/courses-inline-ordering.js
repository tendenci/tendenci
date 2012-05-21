position_field = 'number'; // Name of inline model field (integer) used for ordering. Defaults to "position".

jQuery(function($) {    
    // This script is applied to all TABULAR inlines
    $('div.inline-group div.tabular').each(function() {
        table = $(this).find('table');

        // Drag and drop functionality - only used if a position field exists
        if (position_field != '' && table.find('td').is('.' + position_field))
        {
            // Hide "position"-field (both td:s and th:s)
            $(this).find('td.' + position_field).hide();
            td_pos_field_index = table.find('tbody tr td').index($(this).find('td.' + position_field));
            $(this).find('th:eq(' + (td_pos_field_index-1) + ')').hide();
            
            // Hide "original"-field and set any colspan to 1 (why show in the first case?)
            $(this).find('td.original').hide();
            $(this).find('th[colspan]').removeAttr('colspan');

            // Make table sortable using jQuery UI Sortable
            table.sortable({
                items: 'tr:has(td)',
                tolerance: 'pointer',
                axis: 'y',
                cancel: 'input,button,select,a',
                helper: 'clone',
                update: function() {
                    update_positions($(this));
                }
            });
            
            
            // Re-order <tr>:s based on the "position"-field values.
            // This is a very simple ordering which only works with correct position number sequences,
            // which the rest of this script (hopefully) guarantees.
            rows = [];
            table.find('tbody tr').each(function() {
                position = $(this).find('td.' + position_field + ' input').val();
                rows[position] = $(this);
                
                // Add move cursor to table row.
                table.find('tr:has(td)').css('cursor', 'move')
            });
            
            for (var i in rows) { table.append(rows[i]); } // Move <tr> to its correct position
            update_positions($(this), true);
        }
        else
            position_field = '';
    });
});

// Updates "position"-field values based on row order in table
function update_positions(table, update_ids)
{
    even = true
    num_rows = 0
    position = 0;

    // Set correct position: Filter through all trs, excluding first th tr and last hidden template tr
    table.find('tbody tr:not(.add_template):not(.deleted_row)').each(function() {
        if (position_field != '')
        {
            // Update position field
            $(this).find('td.' + position_field + ' input').val(position + 1);
            position++;
            
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
    });
    
}

// Updates actual id and name attributes of inputs, selects and so on.
// Required for Django validation to keep row order.
function update_id_fields(row, new_position)
{
    // Fix IDs, names etc.
    
    // <select ...>
    row.find('select').each(function() {
        // id=...
        old_id = $(this).attr('id').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('id', new_id)
        
        // name=...
        old_id = $(this).attr('name').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('name', new_id)
    });
    
    // <input ...>
    row.find('input').each(function() {
        // id=...
        old_id = $(this).attr('id').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('id', new_id)
        
        // name=...
        old_id = $(this).attr('name').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('name', new_id)
    });
    
    // <a ...>
    row.find('a').each(function() {
        // id=...
        old_id = $(this).attr('id').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('id', new_id)
    });
    
    // Are there other element types...? Add here.
}

// Replace "Add another question" link in inline with blank question add form link.
jQuery(function($) { 
    $(".ui-sortable tr:last").find('a').replaceWith('<a href="/admin/courses/question/add">Add a Question</a>');
});