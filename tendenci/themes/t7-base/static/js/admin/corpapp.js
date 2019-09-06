// stacked inline fields for corpapp
jQuery(function($) {
	function field_type_toggle(node)
	{
		if (($(node).val()== "section_break") || ($(node).val()== "page_break")){
			// for section and page, hide all fields except admin_only, instruction and css_class
			$(node).closest('fieldset').find('div.inline-fields-to-toggle .form-row')
					.not('div.inline-fields-to-toggle .instruction, div.inline-fields-to-toggle .css_class, div.inline-fields-to-toggle .admin_only').each(function(){
				$(this).hide();
				$(node).closest('fieldset').find('div.inline-fields-to-toggle .admin_only .field-box').not('.field-box:last').hide();
				
			});
			
		}else{
			$(node).closest('fieldset').find('div.inline-fields-to-toggle .form-row').show();
			$(node).closest('fieldset').find('div.inline-fields-to-toggle .admin_only .field-box').not('.field-box:last').show();
			
			if (($(node).val()== "ChoiceField") || ($(node).val()== "MultipleChoiceField")
					|| ($(node).val()== "ChoiceField/django.forms.RadioSelect")
					|| ($(node).val()== "MultipleChoiceField/django.forms.CheckboxInput")){
				$(node).closest('fieldset').find('div.inline-fields-to-toggle .choices').show();
			}else{
				$(node).closest('fieldset').find('div.inline-fields-to-toggle .choices').hide();
			}
			if (($(node).val()== "ChoiceField/django.forms.RadioSelect")
					|| ($(node).val()== "MultipleChoiceField/django.forms.CheckboxInput")){
				$(node).closest('fieldset').find('div.inline-fields-to-toggle .field_layout .field-box:last').show();
			}else{
				$(node).closest('fieldset').find('div.inline-fields-to-toggle .field_layout .field-box:last').hide();
			}
		}
	}	
	
	
	$(document).ready(function() {
	
		// process for all existing fields
		$('div.inline-group > div.inline-related').not('div.inline-related:last').each(function(i) {
			field_type_toggle($(this).find('select[id$=field_type]'));
	    });
		
		$('select[id$=field_type]').on("change", function(){
			field_type_toggle(this);
		});
		
//		$('select[id$=field_type]').bind("change", function(){
//			field_type_toggle(this);
//		
//		});
		
	});
	

});

