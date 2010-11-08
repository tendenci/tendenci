$(document).ready(function () {
	if ($("select[name=type_exp_method_0]").val()== "fixed"){
        $("#rolling-box").hide();
        $("#fixed-box").show();
    }else{
        $("#rolling-box").show();
        $("#fixed-box").hide();
    }
	$("select[name=type_exp_method_0]").change(function(){
		$("#rolling-box").toggle();
		$("#fixed-box").toggle();
	});
});