$(document).ready(function () {
    if ($('input[name=never_expires]').is(':checked')){
        $('div.field-type_exp_method').hide();
    }else{
        $('div.field-type_exp_method').show();
    }
    $("input[name=never_expires]").on("click", function(){
        $('div.field-type_exp_method').toggle("slow");
    });

    if ($("select[name=type_exp_method_0]").val()== "fixed"){
        $("#rolling-box").hide();
        $("#fixed-box").show();
    }else{
        $("#rolling-box").show();
        $("#fixed-box").hide();
    }
    $("select[name=type_exp_method_0]").on("change", function(){
        $("#rolling-box").toggle("slow");
        $("#fixed-box").toggle();
    });
});
