tinyMCEPopup.requireLangPack();

var codemirror;

var CodeDialog = {
  init : function() {
    var f = document.forms[0];
    f.code.value = tinyMCEPopup.editor.getContent();
    
    codemirror = CodeMirror.fromTextArea(f.code, {
      height: "350px",
      width: "680px",
      parserfile: "parsexml.js",
      stylesheet: "js/codemirror/css/xmlcolors.css",
      path: "js/codemirror/js/",
      reindentOnLoad: true, 
      continuousScanning: 500,
      lineNumbers: true
    });
  },

  insert : function() {
    tinyMCEPopup.editor.setContent(codemirror.getCode());
    tinyMCEPopup.close();
  }
};

tinyMCEPopup.onInit.add(CodeDialog.init, CodeDialog);