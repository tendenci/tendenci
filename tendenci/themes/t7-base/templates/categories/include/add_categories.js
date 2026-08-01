(function($){  		
    $('#t-categories-add-category-help-text button').on("click", function(){
        select_box = $(this).closest(".form-group").find('select#id_category');
        var category = prompt('{% trans "Category Name?" %}','').toLowerCase();
        category = category.replace('"','');

        if (category){
        	var option_html = '<option selected="selected" value="' + category + '">' + category + '</option>';
        	select_box.append(option_html);
        }
        return false;
    });
    $('#t-categories-add-subcategory-help-text button').on("click", function(){
        select_box = $(this).closest(".form-group").find('select#id_sub_category');
        var sub_category = prompt('{% trans "Category Name?" %}','').toLowerCase();
        sub_category = sub_category.replace('"','');

        if (sub_category){
        	var option_html = '<option selected="selected" value="' + sub_category + '">' + sub_category + '</option>';
         	select_box.append(option_html);
        }

        return false;
    });
	
})(jQuery);
