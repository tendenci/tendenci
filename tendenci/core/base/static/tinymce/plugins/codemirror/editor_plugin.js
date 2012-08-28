// $Id: editor_plugin.js,v 1.1 2010/03/17 16:48:12 drifter Exp $
(function() {
  tinymce.PluginManager.requireLangPack('codemirror');
  
  tinymce.create('tinymce.plugins.CodeMirrorPlugin', {
    init : function(ed, url) {
      // Register commands
      ed.addCommand('mceCodeMirror', function() {
        ed.windowManager.open({
/*  use this instead for the standalone, non-php version: file : url + '/dialog.html',  */
          file : url + '/dialog.html?path='+escape(tinyMCE.baseURL)+'&random=' + Math.random(),
          width : 750 + parseInt(ed.getLang('codemirror.delta_width', 0)),
          height : 450 + parseInt(ed.getLang('codemirror.delta_height', 0)),
          inline : 1
        }, {
          plugin_url : url
        });
      });

      // Register buttons
      ed.addButton('codemirror', {
        title : ed.getLang('codemirror.desc', 0),
        cmd : 'mceCodeMirror',
        image : url + '/img/html.png'
      });

      ed.onNodeChange.add(function(ed, cm, n) {});
    },

    getInfo : function() {
      return {
        longname : 'CodeMirror Highlighting Editor',
        author : 'Zoltan Varady',
        authorurl : 'http://www.farm.co.hu',
        version : tinymce.majorVersion + "." + tinymce.minorVersion
      };
    }
  });

  // Register plugin
  tinymce.PluginManager.add('codemirror', tinymce.plugins.CodeMirrorPlugin);
})();
