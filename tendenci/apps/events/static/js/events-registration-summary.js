function updateSummaryEntry(prefix, idx, price){
    // update the summary entry in the summary table
    // insert it into the table if it does not exist yet
    var entry_id = '#summary-'+prefix+'-'+idx
    var summary_table = $('#summary-price');
    var entry = $(entry_id);
    var price = parseFloat(price);
    if(entry.length>0){
        entry.find('.item-price').html(price.toFixed(2));
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
    var total_amount = 0.00;
    var discount_amount = parseFloat($('#discount-amount').html());
    var item_price_node;

    for(i=0;i<items.length;i++){
    	item_price_node = $(items[i]).find('.item-price');
    	if (!$(item_price_node).hasClass('free-pass-price')){
    		item_amount = parseFloat($(item_price_node).html());
        	total_amount = total_amount + item_amount;
    	}
    }
    var final_amount = total_amount - discount_amount;
    if (final_amount < 0){
    	final_amount = 0.00;
    }
    $('#total-amount').html(total_amount.toFixed(2));
    $('#summary-total-amount').html(final_amount.toFixed(2));
    $('#final-amount').html(final_amount.toFixed(2));
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
