function tendenciFileManager(field_name, url, type, win) {
	var app_label = tinymce.activeEditor.settings.storme_app_label;
	var model = tinymce.activeEditor.settings.storme_model;
	var object_id = tinymce.activeEditor.settings.app_instance_id;
	
 	var filebrowser = "/files/tinymce-fb/";
	filebrowser += (filebrowser.indexOf("?") < 0) ? "?type=" + type : "&type=" + type;
	if (app_label){
		filebrowser += "&app_label=" + app_label;
	}
	if (model){
		filebrowser += "&model=" + model;
	}
	if (object_id){
		filebrowser += "&object_id=" + object_id;
	}
	
	var title = (type == 'image') ? 'Image ' : 'File ';
	title += 'Gallery | Tendenci';
	tinymce.activeEditor.windowManager.open({
		title : title,
		width : 800,
		height : 550,
		url : filebrowser
		},  {
		window : win,
		input : field_name
	});
	return false;
 }
