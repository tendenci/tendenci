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
function hideShowAddressFields(action="show") {
	const address_fields = [$('#id_place-place'),
							$('#id_place-address'), 
							$('#id_place-city'),
							$('#id_place-state'),
							$('#id_place-zip'),
							$('#id_place-county'),
							$('#id_place-country')];
	if (action =='show'){
		for (let i = 0; i < address_fields.length; i++) {
		  address_fields[i].closest('.form-group').show();
		}
	}else{
		for (let i = 0; i < address_fields.length; i++) {
		  address_fields[i].closest('.form-group').hide();
		}
	}
}
function processVirtual(virtual_field){
	if($(virtual_field).prop('checked')) {
		hideShowAddressFields(action="hide");
    } else {
		hideShowAddressFields(action="show");
    }
}

var virtual_field = $('#id_place-virtual');
processVirtual(virtual_field);
virtual_field.on("change", function() {
	processVirtual(virtual_field);
    /*if($(this).prop('checked')) {
		hideShowAddressFields(action="hide");
    } else {
		hideShowAddressFields(action="show");
    }*/
});