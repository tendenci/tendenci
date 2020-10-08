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
                selector[0].options.length = 0;
                if (!json["error"]){
                    if (json["count"] < 1) {
                        selector.append('<option value="" selected="selected">No sub-categories available</option>');
                    } else {
                        for (var i=0; i<json["count"]; i++) {
                            var pk = json["sub_categories"][i][0];
                            var label = json["sub_categories"][i][1];
                            var option_html = '<option value="' + pk + '">' + label + '</option>';
                            selector.append(option_html);
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
