/*
 * Listen for file (image) resize
 * Resize image at url level -EZ 07/20/2010
 */

event_handler = function(e){
	if (e.type == "mouseup") {
		selection = tinyMCE.activeEditor.selection.getNode();
		if (selection.tagName == "IMG") {
			if (selection.src.indexOf("files") != -1) {
				setTimeout("resize(selection)", 100);
			}
		}
	}
	return true;	
};

resize = function(el) {
	if(el.src.search(/\d+x\d+/) != -1) new_url = el.src.replace(/\d+x\d+/, el.width+'x'+el.height);
	else new_url = el.src + el.width + 'x' + el.height + '/';
    el.setAttribute("src", new_url);
    el.setAttribute("mce_src", new_url);
}