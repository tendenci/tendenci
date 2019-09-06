jQuery.fn.inputFieldText = function(string, hintClass) {
  this.each(function() {
	  if($(this).val().length <= 0)
	  	$(this).addClass(hintClass).val(string);
      $(this).focus(function(){
        if ($(this).val() == string){
          $(this).removeClass(hintClass).val('');
        }
      });
      $(this).blur(function(){
        if ($(this).val() == '' ){
          $(this).addClass(hintClass).val(string);
        }
      });
  });
}
