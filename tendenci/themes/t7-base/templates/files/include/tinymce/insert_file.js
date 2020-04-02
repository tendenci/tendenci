$(document).on("click","button.insert-file",function(){
	item_url = $(this).data("src");
	var args = top.tinymce.activeEditor.windowManager.getParams();
	win = (args.window);
	input = (args.input);
	win.document.getElementById(input).value = item_url;
	top.tinymce.activeEditor.windowManager.close();
});
