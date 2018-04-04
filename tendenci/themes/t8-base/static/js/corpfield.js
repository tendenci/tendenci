$(document).ready(function () {
	var mynode = $('select[name=field_type]');
	show_hide_choices(mynode);

	mynode.change(function(){
		show_hide_choices(this);
	});
});

function show_hide_choices(node)
{
	if (($(node).val()== "ChoiceField") || ($(node).val()== "MultipleChoiceField")
			|| ($(node).val()== "ChoiceField/django.forms.RadioSelect")
			|| ($(node).val()== "MultipleChoiceField/django.forms.CheckboxInput")){
		$('div.choices').show();
	}else{
		$('div.choices').hide();
	}
	if (($(node).val()== "ChoiceField/django.forms.RadioSelect")
			|| ($(node).val()== "MultipleChoiceField/django.forms.CheckboxInput")){
		$('div.field_layout').show();
	}else{
		$('div.field_layout').hide();
	}
}