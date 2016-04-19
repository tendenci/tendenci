(function ($) {
	var callbacks = {
	    'tendenciFileManager' : tendenciFileManager
	};

  function initTinyMCE($e) {
    if ($e.parents('.empty-form').length == 0) {  // Don't do empty inlines
      var mce_conf = $.parseJSON($e.attr('data-mce-conf'));
      if ('media_alt_source' in mce_conf && mce_conf['media_alt_source'] == 'false'){
      	mce_conf['media_alt_source'] = false;
      }
      if ('media_poster' in mce_conf && mce_conf['media_poster'] == 'false'){
      	mce_conf['media_poster'] = false;
      }
      if ('convert_urls' in mce_conf && mce_conf['convert_urls'] == 'false'){
        	mce_conf['convert_urls'] = false;
        }
      
      if ('file_browser_callback' in mce_conf && mce_conf['file_browser_callback'] == 'tendenciFileManager'){
      	// have to convert the string to function, otherwise it won't work'
      	mce_conf['file_browser_callback'] = callbacks['tendenciFileManager'];
      }
      var id = $e.attr('id');
      if ('elements' in mce_conf && mce_conf['mode'] == 'exact') {
        mce_conf['elements'] = id;
      }
      if ($e.attr('data-mce-gz-conf')) {
        tinyMCE_GZ.init($.parseJSON($e.attr('data-mce-gz-conf')));
      }
      if (!tinyMCE.editors[id]) {
        tinyMCE.init(mce_conf);
      }
    }
  }

  $(function () {
    // initialize the TinyMCE editors on load
    $('.tinymce').each(function () {
      initTinyMCE($(this));
    });

    // initialize the TinyMCE editor after adding an inline
    // XXX: We don't use jQuery's click event as it won't work in Django 1.4
    document.body.addEventListener("click", function(ev) {
      if(!ev.target.parentNode || ev.target.parentNode.className.indexOf("add-row") === -1) {
        return;
      }
      var $addRow = $(ev.target.parentNode);
      setTimeout(function() {  // We have to wait until the inline is added
        $('textarea.tinymce', $addRow.parent()).each(function () {
          initTinyMCE($(this));
        });
      }, 0);
    }, true);
  });
}((typeof django === 'undefined' || typeof django.jQuery === 'undefined') && jQuery || django && django.jQuery));
