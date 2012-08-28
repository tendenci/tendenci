/**
 * $Id: editor_plugin_src.js 677 2008-03-07 13:52:41Z spocke $
 *
 * @author Moxiecode
 * @copyright Copyright © 2004-2008, Moxiecode Systems AB, All rights reserved.
 */

(function() {
	// Load plugin specific language pack
	tinymce.PluginManager.requireLangPack('stormeimage');

	tinymce.create('tinymce.plugins.StormeImagePlugin', {
		init : function(ed, url) {

			var app_label = ed.settings.storme_app_label;
			var model = ed.settings.storme_model;
			var instance_id = ed.settings.app_instance_id;

			// Register commands
			ed.addCommand('mceStormImage', function() {
				// Internal image object like a flash placeholder
				if (ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceItem') != -1)
					return;

				ed.windowManager.open({
					//file : url + '/image.html',
					file : '/files/tinymce/?app_label='+ app_label +'&model='+ model +'&instance_id='+ instance_id,

					width : 480 + parseInt(ed.getLang('stormeimage.delta_width', 0)),
					height : 385 + parseInt(ed.getLang('stormeimage.delta_height', 0)),
					inline : 1
				}, {
					plugin_url : url
				});
			});

			// Register buttons
			ed.addButton('image', {
				title : 'stormeimage.desc',
				cmd : 'mceStormImage',
				image : url + '/img/attachment.gif'
			});

			// Add a node change handler, selects the button in the UI when a image is selected
			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('stormeimage', n.nodeName == 'IMG');
			});

		},

		getInfo : function() {
			return {
				longname : 'Advanced image',
				author : 'Moxiecode Systems AB',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/advimage',
				version : tinymce.majorVersion + "." + tinymce.minorVersion
			};
		}
	});

	// Register plugin
	tinymce.PluginManager.add('stormeimage', tinymce.plugins.StormeImagePlugin);
})();