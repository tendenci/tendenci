function toggle_reply_to()
{
	var regconf_enabled = $("#id_regconf-enabled");
	var regconf_replyto = $("#id_regconf-reply_to");
	var regconf_replyto_label = $("label[for=id_regconf-reply_to]");
    if (regconf_enabled.is(":checked")){
    	regconf_replyto.prop('required',true);
    	regconf_replyto_label.addClass("required");
    }else{
    	regconf_replyto.removeAttr('required');
    	regconf_replyto_label.removeClass("required");
    }
}
            
$(function() {
    toggle_reply_to();
     $('#id_regconf-enabled').on("change", function() {
     	toggle_reply_to();
      });
});