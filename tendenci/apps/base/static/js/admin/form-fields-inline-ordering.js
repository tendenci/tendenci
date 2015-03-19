position_field = 'position'; // Name of inline model field (integer) used for ordering. Defaults to "position".

jQuery(document).ready(function($) {
    // This script is applied to all TABULAR inlines
    $('div._inline-group div.tabular').each(function() {
        table = $(this).find('table');

        // Drag and drop functionality - only used if a position field exists
        if (position_field !== '' && table.find('td').is('.field-' + position_field))
        {
            // Hide "position"-field (both td:s and th:s)
            $(this).find('td.field-' + position_field).hide();
            td_pos_field_index = table.find('tbody tr td').index($(this).find('td.field-' + position_field));
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
                    update_positions($(this), true);
                }
            });

            // Re-order <tr>:s based on the "position"-field values.
            // This is a very simple ordering which only works with correct position number sequences,
            // which the rest of this script (hopefully) guarantees.
            rows = [];
            var position_vals = [];
            table.find('tbody tr:not(.empty-form):not(.add-row)').each(function() {
                var pfield = $(this).find('td.field-' + position_field + ' input');
                position = pfield.val();
                /* check duplicate position */
                if(jQuery.inArray(position, position_vals) != -1) { // duplicate exists if != -1
                    position = parseInt(position_vals[position_vals.length-1]) + 1;
                    position = position.toString();
                }
                position_vals.push(position);
                rows[position] = $(this);
                pfield.val(position);


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
        else
            position_field = '';
    });

    $('fieldset .add-row a').click(function(){
        var table = $(this).parents('table');
        var inputs = table.find('tbody tr.dynamic-fields:not(.add_template):not(.deleted_row) .field-position input');
        inputs.each(function(){
            if(this.value == '0'){
                this.value = inputs.length.toString();
            }
        });

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
        $(this).attr('id', new_id);

        // name=...
        old_id = $(this).attr('name').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('name', new_id);
    });

    // <input ...>
    row.find('input').each(function() {
        // id=...
        old_id = $(this).attr('id').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('id', new_id);

        // name=...
        old_id = $(this).attr('name').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('name', new_id);
    });

    // <a ...>
    row.find('a').each(function() {
        // id=...
        old_id = $(this).attr('id').toString();
        new_id = old_id.replace(/([^ ]+\-)[0-9]+(\-[^ ]+)/i, "$1" + new_position + "$2");
        $(this).attr('id', new_id);
    });

    // Are there other element types...? Add here.
}
