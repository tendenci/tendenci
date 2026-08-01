function tendenciFileManager(callback, value, type) {
	var app_label = tinymce.activeEditor.getParam('storme_app_label');
	var model = tinymce.activeEditor.getParam('storme_model');
	var object_id = tinymce.activeEditor.getParam('app_instance_id');
    var fbURL = '/files/tinymce-fb/';
    fbURL += (fbURL.indexOf("?") < 0) ? "?type=" + type.filetype : "&type=" + type.filetype;

    if (app_label){
		fbURL += "&app_label=" + app_label;
	}
	if (model){
		fbURL += "&model=" + model;
	}
	if (object_id){
		fbURL += "&object_id=" + object_id;
	}
	
    var title = (type.filetype == 'image') ? 'Image ' : 'File ';
	title += 'Gallery | Tendenci';
    const instanceApi = tinyMCE.activeEditor.windowManager.openUrl({
        title: title,
        url: fbURL,
        width: 850,
        height: 500,
        onMessage: function(dialogApi, data) {
            callback(data.src, {alt: data.alt});
            instanceApi.close();
        }
    });
    return false;
}
