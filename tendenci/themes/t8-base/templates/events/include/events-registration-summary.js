function commaSeparateNumber(val){
    while (/(\d+)(\d{3})/.test(val.toString())){
      val = val.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
    }
    return val;
}

function removeCommas(val) {
    val = val.toString();
    if (val.indexOf(',') > -1)
        val = val.replace(/\,/g,'');
    return val;
}

function updateSummaryEntry(prefix, idx, price){
    // update the summary entry in the summary table
    // insert it into the table if it does not exist yet
    var entry_id = '#summary-'+prefix+'-'+idx
    var summary_table = $('#summary-price');
    var entry = $(entry_id);
    var price = parseFloat(removeCommas(price));
    if(entry.length>0){
        {% if SITE_GLOBAL_ALLOWDECIMALCOMMAS %}
        var newval = commaSeparateNumber(price.toFixed(2));
        {% else %}
        var newval = price.toFixed(2).toString();
        {% endif %}
        entry.find('.item-price').html(newval);
    }else{
        var row = $('#summary-item-hidden').clone(true);
        row.addClass('summary-'+prefix);
        row.attr('id', 'summary-'+prefix+'-'+idx);
        {% if SITE_GLOBAL_ALLOWDECIMALCOMMAS %}
        var newval = commaSeparateNumber(price.toFixed(2));
        {% else %}
        var newval = price.toFixed(2).toString();
        {% endif %}
        row.find('.item-price').html(newval);
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
    var discount_amount = parseFloat(removeCommas($('#discount-amount').html()));
    var item_price_node;

    for(i=0;i<items.length;i++){
        item_price_node = $(items[i]).find('.item-price');
        if (!$(item_price_node).hasClass('free-pass-price')){
            item_amount = parseFloat(removeCommas($(item_price_node).html()));
            total_amount = total_amount + item_amount;
        }
    }
    var final_amount = total_amount - discount_amount;
    if (final_amount < 0){
        final_amount = 0.00;
    }

    {% if SITE_GLOBAL_ALLOWDECIMALCOMMAS %}
    var new_total_amount = commaSeparateNumber(total_amount.toFixed(2));
    var new_final_amount = commaSeparateNumber(final_amount.toFixed(2));
    {% else %}
    var new_total_amount = total_amount.toFixed(2).toString();
    var new_final_amount = final_amount.toFixed(2).toString();
    {% endif %}

    $('#total-amount').html(new_total_amount);
    $('#summary-total-amount').html(new_final_amount);
    $('#final-amount').html(new_final_amount);
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
