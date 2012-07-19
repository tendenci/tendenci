function mainmenu(){
$("#menu ul a").removeAttr('title');
$("#menu ul ul ").css({display: "none"}); // Opera Fix
$("#menu ul li").hover(function(){
		$(this).find('ul:first').css({visibility: "visible",display: "none"}).show(400);
		},function(){
		$(this).find('ul:first').css({visibility: "hidden"});
		});
}

 
 
 $(document).ready(function(){					
	mainmenu();
});