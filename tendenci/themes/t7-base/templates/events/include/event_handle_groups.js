function populate_primary_group()
{
	var primary_group_id = $('#id_primary_group option:selected')[0].value;
	// console.log(primary_group_id)
	$('#id_primary_group').html('');
	$('#id_groups option:selected').each(function(){
		if (primary_group_id && primary_group_id == this.value){
			$('#id_primary_group').append('<option value="' + this.value + '" selected="">' + this.innerText  + '</option>');
		}else{
			$('#id_primary_group').append('<option value="' + this.value + '">' + this.innerText  + '</option>');
		}
	});
}

$(function() {
    {% if not MODULE_EVENTS_ALLOWMULTIGROUPS %}
	// Remove multi-select option from groups
    $('select#id_groups').prop('multiple', false );
    $('#id_groups').next('span.help-block').hide();
    {% else %}
    // Populate primary group with the selected groups from the groups field
    //populate_primary_group();
    $('#id_groups').on('change', function(){
	    populate_primary_group();
    });
    {% endif %}
});