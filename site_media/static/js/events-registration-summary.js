function updateSummaryEntry(prefix, idx, price){
    // update the summary entry in the summary table
    // insert it into the table if it does not exist yet
    var entry_id = '#summary-'+prefix+'-'+idx
    var summary_table = $('#summary-price');
    var entry = $(entry_id);
    if(entry.length>0){
        entry.find('.price').html(price.toFixed(2));
    }else{
        var row = $('#summary-item-hidden').clone(true);
        row.addClass('summary-'+prefix);
        row.attr('id', 'summary-'+prefix+'-'+idx);
        row.find('.item-price').html(price.toFixed(2));
        row.find('.item-label').html(prefix + "#" + (idx+1));
        summary_table.append(row);
    }
    updateSummaryTotal();
}

function removeSummaryEntry(prefix, idx){
    var entry = $('#summary-'+prefix+'-'+idx);
    entry.remove();
    updateSummaryIndex(prefix);
    updateSummaryTotal();
}

function updateSummaryTotal(){
    // update the total
    var summary_table = $('#summary-price');
    var items = $('#summary-price tr');
    var total_amount = 0;
    for(i=0;i<items.length;i++){
        item_amount = parseFloat($(items[i]).find('.item-price').html());
        total_amount = total_amount + item_amount;
    }
    $('#total-amount').html(total_amount.toFixed(2));
    $('#summary-total-amount').html(total_amount.toFixed(2));
    $('#final-amount').html(total_amount.toFixed(2));
}

function updateSummaryIndex(prefix){
    var summary_table = $('#summary-price');
    var items = $('.summary-'+prefix);
    for(i=0;i<items.length;i++){
        var row = $(items[i]);
        row.attr('id', 'summary-'+prefix+'-'+i);
        row.find('.item-label').html(prefix + "#" + (i+1));
    }
}
