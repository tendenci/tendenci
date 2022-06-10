//Populate sub categories with value of main category
$(document).ready(function() {
    $('select#id_cat').on("change", function() {
        // Get sub categories through ajax
        $.post(
            "{% url "photos.get_sub_categories" %}",
            {'cat':$(this).val(),
             'csrfmiddlewaretoken':$('input[name="csrfmiddlewaretoken"]').val(),},
            function(data, textStatus, jqXHR){
                var json = JSON.parse(data);
                var selector = $('select#id_sub_cat');
                selector[0].options.length = 0;
                if (!json["error"]){
                    if (json["count"] < 1) {
                        selector.append('<option value="" selected="selected">No sub-categories available</option>');
                    } else {
                        selector.append('<option value="" selected="selected">-----------</option>');
                        for (var i=0; i<json["count"]; i++) {
                            var pk = json["sub_cats"][i][0];
                            var label = json["sub_cats"][i][1];
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
})
