$(document).ready(function() {
    // Set this to the name of the column holding the ordering
    var pos_field = 'ordering';

    // Determine the column number of the ordering field
    var pos_col = null;

    var cols = $('#result_list tbody tr:first').children()

    for (i = 0; i < cols.length; i++) {
        var inputs = $(cols[i]).find('input[name*=' + pos_field + ']')

        if (inputs.length > 0) {
            // Found!
            var pos_col = i;
            break;
        }
    }

    if (pos_col == null) {
        return;
    }

    // Some visual enhancements
    var header = $('#result_list thead tr').children()[pos_col]
    $(header).css('width', '1em')
    $(header).children('a').text('Move')

    // Hide ordering field
    $('#result_list tbody tr').each(function(index) {
        var pos_td = $(this).children()[pos_col]
        var input = $(pos_td).children('input').first()
        //input.attr('type', 'hidden')
        input.hide()

        var label = $('<span><img src="/static/themes/t7-base/images/icons/drag_icon_16x16.png" alt="drag icon 16x16" title="drag icon 16x16" /></span>')
        $(pos_td).append(label)
    });

    // Determine sorted column and order
    var sorted = $('#result_list thead th.sorted')
    var sorted_col = $('#result_list thead th').index(sorted)
    var sort_order = sorted.hasClass('descending') ? 'desc' : 'asc';

    if (sorted_col != pos_col) {
        // Sorted column is not ordering column, bail out
        console.info("Sorted column is not %s, bailing out", pos_field);
        return;
    }

    $('#result_list tbody tr td span').css('cursor', 'move')

    // Make tbody > tr sortable
    $('#result_list tbody').sortable({
        axis: 'y',
        items: 'tr',
        cursor: 'move',
        update: function(event, ui) {
            var item = ui.item
            var items = $(this).find('tr').get()

            if (sort_order == 'desc') {
                // Reverse order
                items.reverse()
            }

            $(items).each(function(index) {
                var pos_td = $(this).children()[pos_col]
                var input = $(pos_td).children('input').first()
                var label = $(pos_td).children('span').first()

                input.attr('value', index)
                label.html('<img src="/static/themes/t7-base/images/icons/drag_icon_16x16.png" />')
            });

            // Update row classes
            $(this).find('tr').removeClass('row1').removeClass('row2')
            $(this).find('tr:even').addClass('row1')
            $(this).find('tr:odd').addClass('row2')
            if ($('ul.messagelist').length < 1) {
            $('div.breadcrumbs').append('<ul class="messagelist"><li class="warning">Be sure to click save to update the order.</li></ul>');
            } else {
            $('ul.messagelist').html('<li class="warning">Be sure to click save to update the order.</li>');
            }
        }
    });
});
