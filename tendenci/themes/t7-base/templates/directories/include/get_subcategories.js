// get sub categories based on category
$.ajaxSetup({beforeSend: function(xhr, settings){
	 xhr.setRequestHeader('X-CSRFToken',
	                      '{{ csrf_token }}'); 
}});
(function($) {
$(document).ready(function(){
    $('select#id_cats').on("change", function() {
        $.post(
            "{% url "directory.get_subcategories" %}",
            {'categories': $(this).val().join(),
             'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val(),},
            function(data, textStatus, jqXHR){
                var json = JSON.parse(data);
                var selector = $('select#id_sub_cats');
                //selector[0].options.length = 0;
                selector.children().remove("optgroup");
                if (!json["error"]){
                    if (json["count"] < 1) {
                        selector.append('<option value="" selected="selected">No sub-categories available</option>');
                    } else {
	                    for (var i=0; i<json["count"]; i++) {
		                    var cat_name = json['sub_categories'][i].cat_name;
                            var this_optgroup =  $('<optgroup label="' + cat_name + '">');
		                    var sub_cats = json['sub_categories'][i].sub_cats;
		                    for( let j in sub_cats ){
			                    this_optgroup.append('<option value="' + sub_cats[j][0] + '">' + sub_cats[j][1] + '</option>');
							}
							selector.append(this_optgroup);
						}
                    }
                } else {
                    selector.append('<option value="" selected="selected">Please choose a category first</option>');
                }
            }
        );
    });
});
}(jQuery));
