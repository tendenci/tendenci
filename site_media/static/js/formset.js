function cloneForm(selector, type) {
    var newElement = $(selector).clone(true);
    
    if ($(selector).hasClass('alt')) {
        newElement.removeClass('alt');
    } 
    else {
        newElement.addClass('alt');
    }
    
    var total = $('#id_' + type + '-TOTAL_FORMS').val();
    
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
    });
    
    newElement.find('label').each(function() {
        var newFor = $(this).attr('for').replace('-' + (total-1) + '-','-' + total + '-');
        $(this).attr('for', newFor);
    });
    
    total++;
    
    $('#id_' + type + '-TOTAL_FORMS').val(total);
    
    $(selector).after(newElement);
}
