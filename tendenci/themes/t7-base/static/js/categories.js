$(document).ready(function(){
    $('.add-category').on("click", function(){
        select_box = $(this).parent().prev();
        var category = prompt('Category Name?','').toLowerCase();
        category = category.replace('"','')
        var option_html = '<option selected="selected" value="' + category + '">' + category + '</option>';
        if (category) select_box.append(option_html)
        return false;
    });
    $('.add-sub-category').on("click", function(){
        select_box = $(this).parent().prev();
        var sub_category = prompt('Category Name?','').toLowerCase();
        sub_category = sub_category.replace('"','')
        var option_html = '<option selected="selected" value="' + sub_category + '">' + sub_category + '</option>';
        if (sub_category) select_box.append(option_html)
        return false;
    });
});
