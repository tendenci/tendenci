//formset index update
function updateFormIndex(e, prefix, idx){
    var id_regex = new RegExp('(' + prefix + '-\\d+)');
    var replacement = prefix + '-' + idx
    var e = $(e);
    if (e.attr("for")){
        var _for = e.attr('for');
        e.attr("for", _for.replace(id_regex, replacement));
    }
    if (e.attr('id')) {
        var _id = e.attr('id');
        e.attr('id', _id.replace(id_regex, replacement));
    }
    if (e.attr('name')){
        var _name = e.attr('name');
        e.attr('name', _name.replace(id_regex, replacement));
    }
    if (e.attr('class')){
        var _class = e.attr('class');
        e.attr('class', _class.replace(id_regex, replacement));
    }
}

function addAddon(prefix, addon, container){
    var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
    var row = $('#addon-hidden').clone(true).get(0);
    // place proper class
    $(row).addClass('addon-form');
    
    // update id attr
    var replacement = prefix + '_' + formCount
    $(row).attr('id',replacement);
    
    $(row).find(".form-field").children().each(function() {
        updateFormIndex($(this), prefix, formCount);
    });
    
    $(row).find(".form-field").children().children().children().each(function() {
        updateFormIndex($(this), prefix, formCount);
        if($(this).attr("name")==(prefix+"-"+formCount+"-addon")){
            // assign addon selected
            $(this).val(addon['pk'])
        }else{
            var field_name = $(this).attr("name");
            if(field_name){
                var option_name = field_name.split(prefix+"-"+formCount+"-")[1]
                if(!(option_name[0] == addon['pk'])){
                    $(this).parent().parent().hide();
                }
            }
        }
    });
    
    // insert as last element into form list
    $(container).append(row);
    
    $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
    
    return false;
}

//ADDON CONTROLS
$(document).ready(function(){
    var container = $('.addon-forms')
    container.find('.addon-form').each(function(){
        var addon_pk = $(this).find('.addon-input').val()
        $(this).find(".form-field").children().children().children().each(function() {
            if(!$(this).hasClass('addon-input')){
                var field_name = $(this).attr("name");
                if(field_name){
                    var option_name = field_name.split("-")[2]
                    if(!(option_name[0] == addon_pk)){
                        $(this).parent().parent().hide();
                    }
                }
            }
        });
    });
    
    $("#add-addons-button").click(function(){
        var addon = $('input:radio[name=add-addons]:checked');
        var addon_d = {};
        if(addon.val()){
            addon_num = parseInt($("#add-addons-number").val());
            addon_d['quantity'] = addon.attr('quantity');
            addon_d['price'] = addon.attr('price');
            addon_d['title'] = addon.attr('title');
            addon_d['pk'] = addon.val();
            addon_d['is_public'] = addon.attr('is_public');
            for(var i=0; i<addon_num; i++){
                addAddon('addon', addon_d, container);
            }
        } else {
            alert("Please select an addon first.");
        }
    });
});
