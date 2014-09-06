//Populate sub categories with value of main category
$('select#id_file_cat').change(function() {
    // Get sub categories through ajax
    $.post(
        "{% url file.get_categories %}",
        {'category':$(this).val(),
         'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val(),},
        function(data, textStatus, jqXHR){
            var json = $.parseJSON(data);
            var selector = $('select#id_file_sub_cat');
            selector[0].options.length = 0;
            if (!json["error"]){
                if (json["count"] < 1) {
                    selector.append('<option value="" selected="selected">No sub-categories available</option>');
                } else {
                    selector.append('<option value="" selected="selected">-----------</option>');
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