//Populate location with value of place
$('select#id_place-place').on("change", function() {
    if($(this).val()) {
        //Get values of place through ajax
        $.post(
            "{% url "event.get_place" %}",
            {
                'id':$(this).val(),
            },
            function(data, textStatus, jqXHR){
                json = JSON.parse(data);
                if (!json["error"]){
                    $('input#id_place-name').val(json["name"]);
                    $('textarea#id_place-description').html(json["description"]);
                    $('iframe#id_place-description_ifr').contents().find("body#tinymce").html(json["description"]);
                    $('input#id_place-address').val(json["address"]);
                    $('input#id_place-city').val(json["city"]);
                    $('input#id_place-state').val(json["state"]);
                    $('input#id_place-zip').val(json["zip"]);
                    $('input#id_place-country').val(json["country"]);
                    $('input#id_place-url').val(json["url"]);
                }
            }
        );
    }
});
