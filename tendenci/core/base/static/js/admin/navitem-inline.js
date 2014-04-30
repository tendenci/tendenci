$(document).ready(function() {
    var itemTable = $("#navitem_set-group").find('table');

    itemTable.find('td.field-level').each(function() {
        var label = $('<span class="levelBtn levelLeft"></span><span class="levelBtn levelRight"></span>');
        $(this).append(label);
        var level = parseInt($(this).find('input[type="hidden"]').val());
        var sibling = $(this).next('td');
        sibling.css('padding-left', (level*20)+'px');
    });


    initEvents(itemTable);

    $('tr.add-row a').click(function() {
        var table = $(this).parents('table');
        var inputs = table.find('tbody tr.dynamic-navitem_set:not(.add_template):not(.deleted_row) .field-position input');
        inputs.each(function(){
            if(this.value == '0'){
                this.value = inputs.length.toString();
            }
        });
        initEvents(itemTable);
    });
});

function initEvents(table) {

    // Rebind click events
    table.find('span.levelLeft').unbind('click');
    table.find('span.levelLeft').click(function() {
        var parent = $(this).parents('td.field-level');
        var levelInput = parent.find('input[type="hidden"]');
        var level = parseInt(levelInput.val()) - 1;
        var sibling = parent.next('td');
        if (level > -1 ) {
            sibling.css('padding-left', (level*20)+'px');
            levelInput.val(level);
        }
    });

    table.find('span.levelRight').unbind('click');
    table.find('span.levelRight').click(function() {
        var parent = $(this).parents('td.field-level');
        var levelInput = parent.find('input[type="hidden"]');
        var level = parseInt(levelInput.val()) + 1;
        var sibling = parent.next('td');
        if (level < 5 ) {
            sibling.css('padding-left', (level*20)+'px');
            levelInput.val(level);
        }
    });

}
