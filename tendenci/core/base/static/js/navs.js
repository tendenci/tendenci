function updateElementIndex(el, prefix, ndx){
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + ndx;
    if ($(el).attr("for")) $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
    if (el.id) el.id = el.id.replace(id_regex, replacement);
    if (el.name) el.name = el.name.replace(id_regex, replacement);
}

apply_delete = function(thing){
    thing.click(function(){
        var total = $("#id_form-TOTAL_FORMS").val();
        $(this).parent().parent().remove();
        var items = $("#nav-items").find(".nav-item");
        for(i=0;i<total-1;i++){
            var inputs = $(items[i]).find('input');
            for(j=0;j<inputs.length;j++){
                updateElementIndex(inputs[j], 'form', i);
            }
            $($(items[i]).find('#id_form-'+i+'-position')).val(i);
        }
        $("#id_form-TOTAL_FORMS").val(total-1);
        return false;
    });
}

apply_toggle = function(thing){
    thing.click(function(){
        $(this).parent().find('.nav-item-detail').toggle();
        $(this).find('.linklabel').html($(this).parent().find('input[name*="-label"]').val());
        var str = $(this).html();
        var help_str = $(this).find(".helpertext").html();
        if (str.indexOf("-") >= 0) {
            $(this).html(str.replace('-', '+'));
            $(this).find(".helpertext").html(help_str.replace('collapse', 'edit'));
        }
        if (str.indexOf("+") >= 0) {
            $(this).html(str.replace('+', '-'));
            $(this).find(".helpertext").html(help_str.replace('edit', 'collapse'));
        }
        return false;
    });
}

apply_move_left = function(thing){
    thing.click(function(){
        var level = parseInt($($($(this).parent()).find('.level input')).val()) - 1;
        if (level > -1){
            $($(this).parent()).css('margin-left', (level*20)+'px');
            $($($(this).parent()).find('.level input')).val(level)
        }
        return false;
    });
}

apply_move_right = function(thing){
    thing.click(function(){
        var level = parseInt($($($(this).parent()).find('.level input')).val()) + 1;
        if (level < 5){
            $($(this).parent()).css('margin-left', (level*20)+'px');
            $($($(this).parent()).find('.level input')).val(level);
        }
        return false;
    });
}

function showResponse(response, status, xhr, $form)  {
    if (response.error) {
        alert("An error occured");
    } else {
        form_number = parseInt($("#id_form-TOTAL_FORMS").val())
        pages = response.pages
        for(i=0;i<pages.length;i++){
            var items = $("#nav-items");
            var item = $("#base");
            //copy the template form
            var clone = item.clone();
            //customize the form based on the page info
            clone.attr('id', '')
            clone.show();
            clone.find('#id_form-0-id').removeAttr('value');
            clone.find('.url-field').val(pages[i].url);
            clone.find('#id_form-0-label').val(pages[i].label);
            clone.find('.nav-item-label b').html("+ "+pages[i].label);
            clone.find('#id_form-0-page').val(pages[i].id);
            clone.find('#id_form-0-title').val(pages[i].label);
            clone.find('#id_form-0-position').val(form_number);
            clone.find('.url-field').attr('disabled', 'disabled');

            //relace the names and ids of the elements in the form
            //clone.find('#id_form-0-id').attr('name', 'form-' + form_number + '-id');
            clone.find('#id_form-0-id').attr('name', 'form-' + form_number + '-id');
            clone.find('#id_form-0-label').attr('name', 'form-' + form_number + '-label');
            clone.find('#id_form-0-title').attr('name', 'form-' + form_number + '-title');
            clone.find('#id_form-0-css').attr('name', 'form-' + form_number + '-css');
            clone.find('#id_form-0-page').attr('name', 'form-' + form_number + '-page');
            clone.find('#id_form-0-position').attr('name', 'form-' + form_number + '-position');
            clone.find('#id_form-0-level').attr('name', 'form-' + form_number + '-level');

            //clone.find('#id_form-0-id').attr('id', 'id_form-' + form_number + '-id');
            clone.find('#id_form-0-id').attr('id', 'form-' + form_number + '-id');
            clone.find('#id_form-0-label').attr('id', 'id_form-' + form_number + '-label');
            clone.find('#id_form-0-title').attr('id', 'id_form-' + form_number + '-title');
            clone.find('#id_form-0-css').attr('id', 'id_form-' + form_number + '-css');
            clone.find('#id_form-0-page').attr('id', 'id_form-' + form_number + '-page');
            clone.find('#id_form-0-position').attr('id', 'id_form-' + form_number + '-position');
            clone.find('#id_form-0-level').attr('id', 'id_form-' + form_number + '-level');

            //apply the click effects
            clone.find('.nav-item-label').html(clone.find('.nav-item-label').html()+"&nbsp;<span class='helpertext'>(edit)</span>");
            apply_toggle(clone.find('.nav-item-label'));
            apply_delete(clone.find('.item-delete'));
            apply_move_left(clone.find('.nav-move-left'));
            apply_move_right(clone.find('.nav-move-right'));
            //append to the formset
            items.append(clone);
            //increment id count
            form_number++;
        }
        $("#id_form-TOTAL_FORMS").val(form_number);
    }
}

$(document).ready(function(){
    $('#navs-search-box').keyup(function(){
        // hide all pages that do not match search-box's value
        var val = $('#navs-search-box').val().toLowerCase();
        var pages = $('.page-select li');
        for(i=0;i<pages.length;i++){
            if($(pages[i]).html().toLowerCase().indexOf(val)==-1){
                $(pages[i]).hide();
            }else{
                $(pages[i]).show();
            }
        }
    });

    //initialize the formset details and events
    //override and set the initial number of forms to be 0
    //this is to avoid some validation bugs with the dynamic add/delete
    //of the forms.
    var initial = $("#id_form-INITIAL_FORMS").val(0);
    var total = $("#id_form-TOTAL_FORMS").val();
    var items = $("#nav-items").find(".nav-item");
    var item;

    for(i=0;i<total;i++){
        var level = $($(items[i]).find('.level input')).val();
        $(items[i]).css('margin-left', (level*20)+'px');
    }

    $('#base').hide();
    $('.nav-item-detail').hide();

    apply_toggle($('.nav-item-label'));
    apply_delete($('.item-delete'));
    apply_move_left($('.nav-move-left'));
    apply_move_right($('.nav-move-right'));

    //custom form add
    $('#add-custom').click(function(){
        form_number = parseInt($("#id_form-TOTAL_FORMS").val());
        items = $("#nav-items");
        item = $("#base");
        //copy the template form
        clone = item.clone();
        //set default values to the form
        clone.attr('id', '');
        clone.show();
        clone.find('.nav-item-detail').show();
        clone.find('#id_form-0-position').val(form_number);

        //relace the names and ids of the elements in the form
        //clone.find('#id_form-0-id').attr('name', 'form-' + form_number + '-id');
        clone.find('#id_form-0-id').attr('name', 'form-' + form_number + '-id');
        clone.find('#id_form-0-label').attr('name', 'form-' + form_number + '-label');
        clone.find('#id_form-0-title').attr('name', 'form-' + form_number + '-title');
        clone.find('#id_form-0-css').attr('name', 'form-' + form_number + '-css');
        clone.find('#id_form-0-page').attr('name', 'form-' + form_number + '-page');
        clone.find('#id_form-0-position').attr('name', 'form-' + form_number + '-position');
        clone.find('#id_form-0-level').attr('name', 'form-' + form_number + '-level');
        clone.find('#id_form-0-url').attr('name', 'form-' + form_number + '-url');

        //clone.find('#id_form-0-id').attr('id', 'id_form-' + form_number + '-id');
        clone.find('#id_form-0-id').attr('id', 'form-' + form_number + '-id');
        clone.find('#id_form-0-label').attr('id', 'id_form-' + form_number + '-label');
        clone.find('#id_form-0-title').attr('id', 'id_form-' + form_number + '-title');
        clone.find('#id_form-0-css').attr('id', 'id_form-' + form_number + '-css');
        clone.find('#id_form-0-page').attr('id', 'id_form-' + form_number + '-page');
        clone.find('#id_form-0-position').attr('id', 'id_form-' + form_number + '-position');
        clone.find('#id_form-0-level').attr('id', 'id_form-' + form_number + '-level');
        clone.find('#id_form-0-url').attr('id', 'id_form-' + form_number + '-url');

        //apply the click effects
        clone.find('.nav-item-label').html("- <span class='linklabel'>Item " + (form_number+1) + "</span>&nbsp;<span class='helpertext'>(collapse)</span>");
        apply_toggle(clone.find('.nav-item-label'));
        apply_delete(clone.find('.item-delete'));
        apply_move_left(clone.find('.nav-move-left'));
        apply_move_right(clone.find('.nav-move-right'));
        //append to the formset
        items.append(clone);
        //increment id count
        form_number++;
        $("#id_form-TOTAL_FORMS").val(form_number);
    });

    //when pages are chosen to be included in the nav an ajax call will be triggered
    //the ajax will retrieve info from the chosen pages and then append additional forms
    //into the nav item form set.
    var options = {
        success: showResponse,
        error: showResponse,
        dataType: 'json',
        clearForm: true,
        resetForm: true
    };

    $('#page-select').ajaxForm(options);

    //set the nav items to become sortable
    $("#nav-items").sortable({
        cursor: 'move',
        update: function(event, ui){
                items = $(this).find('.nav-item');
                for(i=0;i<items.length;i++){
                    input = $($(items[i]).find('.position input'));
                    input.attr('value', i);
                }
            }
    });
});
