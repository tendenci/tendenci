jQuery(function($) {
    $("div.inline-group").sortable({ 
        axis: 'y',
        placeholder: 'ui-state-highlight', 
        forcePlaceholderSize: 'true', 
        items: '.row1, .row2', 
        update: update
    });
    //$("div.inline-group").disableSelection();
});
function update() {
    $('.row1, .row2').each(function(i) {
        $(this).find('input[id$=position]').val(i+1);
    });
}
jQuery(document).ready(function($){
	// hide position
	var position_index = $('div.inline-related').find('td.position').index();
	$('div.inline-related').find('td.position').hide();
	$('div.inline-related').find('th:nth-child(' + position_index +')').hide();
	
	$('div.inline-related tr').css('cursor','move');
	
    $('.add-row a').click(update);
    
    $('#customregform_form').submit(function() {
        update();
    });
});