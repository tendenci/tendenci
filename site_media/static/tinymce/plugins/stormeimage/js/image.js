var ImageDialog = {
	preInit : function() {
		var url;

		// pass custom variables from initialization
		this.storme_app_label = tinyMCEPopup.editor.settings.storme_app_label;
		this.storme_model = tinyMCEPopup.editor.settings.storme_model;
		this.storme_instance_id = tinyMCEPopup.editor.settings.app_instance_id;

		tinyMCEPopup.requireLangPack();

		if (url = tinyMCEPopup.getParam("external_image_list_url"))
			document.write('<script language="javascript" type="text/javascript" src="' + tinyMCEPopup.editor.documentBaseURI.toAbsolute(url) + '"></script>');
	},

	init : function(ed) {
		var f = document.forms[0], nl = f.elements, ed = tinyMCEPopup.editor, dom = ed.dom, n = ed.selection.getNode();
		tinyMCEPopup.resizeToInnerSize();
		this.fillClassList('class_list');
		TinyMCE_EditableSelects.init();

		if (n.nodeName == 'IMG') {

			this.n = n;

			mcTabs.displayTab('imageedit_tab','imageedit_panel');
			$(".edit_src").attr({src:dom.getAttrib(n, 'src')});

			nl.edit_title.value = dom.getAttrib(n, 'title');
			nl.edit_align.value = this.getAttrib(n, 'align')

			nl.edit_vspace.value = this.getAttrib(n, 'vspace');
			nl.edit_hspace.value = this.getAttrib(n, 'hspace');
			nl.edit_width.value = this.getAttrib(n, 'width');
			nl.edit_height.value = this.getAttrib(n, 'height');

			// margin attributes
			nl.edit_float.value = dom.getStyle(n, 'float');
			nl.edit_top_margin.value = dom.getStyle(n, 'margin-top');
			nl.edit_right_margin.value = dom.getStyle(n, 'margin-right');
			nl.edit_bottom_margin.value = dom.getStyle(n, 'margin-bottom');
			nl.edit_left_margin.value = dom.getStyle(n, 'margin-left');

			nl.style.value = dom.getAttrib(n, 'style');

			if (ed.settings.inline_styles) {
				// Move attribs to styles
				if (dom.getAttrib(n, 'align'))
					this.updateStyle('align');

				if (dom.getAttrib(n, 'vspace'))
					this.updateStyle('vspace');

				if (dom.getAttrib(n, 'hspace'))
					this.updateStyle('hspace');

				if (dom.getAttrib(n, 'border'))
					this.updateStyle('border');
			}
		}
		else {
			this.n = null;
			$("#imageedit_tab").hide();
		}

		// If option enabled default constrain proportions to checked
		if (ed.getParam("stormeimage_constrain_proportions", true))
			f.constrain.checked = true;

		// Check swap image if valid data
		if (nl.onmouseoversrc.value || nl.onmouseoutsrc.value)
			this.setSwapImage(true);
		else
			this.setSwapImage(false);

		this.changeAppearance();
		this.showPreviewImage(nl.src.value, 1);
	},

	remove_image : function() {
		var ed = tinyMCEPopup.editor, f = document.forms[0], nl = f.elements, v, args = {};
		var dom = ed.dom, n = ed.selection.getNode();

		n = this.n;

		if (n.nodeName == 'IMG') {
			dom.remove(n);
			ed.execCommand('mceRepaint');
		}

		tinyMCEPopup.close();
	},

	delete_image : function(obj, image_id) {
		var item_wrap = $(obj).parents('.photo-wrapper')[0]

		$(item_wrap).parent().parent().slideUp("fast", function(){$(this).remove();});
		$("#photo-queue").html($("#fsUploadProgress").children().length-1); // decrement count on screen

		$.ajax({
			type: "POST",
			cache: false,
			data: ({ajax : 1}),
			url: "/files/delete/"+ image_id +"/",
			complete: function(XMLHttpRequest, textStatus){
				// do something after complete
			}
		});
	},

	update : function() {
		var ed = tinyMCEPopup.editor, f = document.forms[0], nl = f.elements, v, args = {};
		var n = ed.selection.getNode();

		n = this.n;
        
		var img_src = $(".edit_src").attr("src");
		var img_title = nl.edit_title.value;
		var img_align = nl.edit_align.value;
		var img_vspace = nl.edit_vspace.value;
		var img_hspace = nl.edit_hspace.value;
		var img_width = nl.edit_width.value;
		var img_height = nl.edit_height.value;
        var img_ratio = $(nl.edit_ratio).is(':checked');
        
        var url_parts = img_src.split('/');
        var img_id = url_parts[2];
        
        if(img_ratio){
            // get original dimensions of image from image list
            var orig_height = $('#file_'+img_id+'_height').val();
            var orig_width = $('#file_'+img_id+'_width').val();
            var old_height = this.getAttrib(n, 'height');
            var old_width = this.getAttrib(n, 'width');
            
            // maintain proportions
            if(img_width > old_width){
                // Resize with width
                img_height = parseInt(orig_height * img_width / orig_width);
            }else{
                // Resize with height instead
                img_width = parseInt(orig_width * img_height / orig_height);
            }
        }
        
        // update url to correct size
        img_src = url_parts[0] + '/' + url_parts[1] + '/' + url_parts[2] + '/' + img_width + 'x' + img_height;
        
		// set the styles
		ed.dom.setStyle(n, 'float', nl.edit_float.value);
		ed.dom.setStyle(n, 'margin-top', nl.edit_top_margin.value + 'px');
		ed.dom.setStyle(n, 'margin-right', nl.edit_right_margin.value + 'px');
		ed.dom.setStyle(n, 'margin-bottom', nl.edit_bottom_margin.value + 'px');
		ed.dom.setStyle(n, 'margin-left', nl.edit_left_margin.value + 'px');

		tinymce.extend(args, {
			src : img_src,
			title : img_title,
			alt : img_title,
			vspace : img_vspace,
			hspace : img_hspace,
			width : img_width,
			height : img_height,
			align : img_align
		});
		
		if(args.src.length > 0){
			ed.dom.setAttribs(n, args);
			ed.undoManager.add();
			ed.execCommand('mceRepaint');
			n = ed.selection.select(n);
		}
	},

	insert : function(obj, file_id) {
		var ed = tinyMCEPopup.editor, args = {};
		var item_wrap = $(obj).parents('.photo-wrapper')[0]

		var icon_url = $(item_wrap).find("input[name='icon_url']").val();
		var filename = $(item_wrap).find("input[name='filename']").val();
		var file_url = $(item_wrap).find("input[name='file_url']").val();
		var file_download_url = $(item_wrap).find("input[name='file_download_url']").val();

		if(icon_url != 'None'){
			var file_element = '<div class="t5_file"> '+ 
				'<a href="'+ file_download_url +'">'+
				'<img src="'+ icon_url +'" /> ' + '</a> ' +
				'<a href="'+ file_download_url +'">'+ filename +'</a> </div>';	
		}
		else {
			var file_element = '<div class="t5_file"> '+ 
				'<a href="'+ file_download_url +'">'+ filename +'</a> </div>';	
		}

		ed.execCommand('mceInsertContent', false, file_element);
		ed.undoManager.add();
	},

	insert_image : function(obj, file_id) {
		var ed = tinyMCEPopup.editor, args = {}, width;
		var item_wrap = $(obj).parents('.photo-wrapper')[0]

		var icon_url = $(item_wrap).find("input[name='icon_url']").val();
		var filename = $(item_wrap).find("input[name='filename']").val();
		var file_url = $(item_wrap).find("input[name='file_url']").val();
		var file_width = $(item_wrap).find("input[name='file_width']").val();
		var file_height = $(item_wrap).find("input[name='file_height']").val();

		var width = file_width;
		var height = file_height;
		if(width > 400) {
			width = 400
			height = ((width*file_height) / file_width);
		}

		// default img attributes
		tinymce.extend(args, {
			src : file_url,
			title : filename,
			alt : filename,
			width: width,
			height: height
		});

		ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : true});
		ed.dom.setAttribs('__mce_tmp', args);
		ed.dom.setAttrib('__mce_tmp', 'id', '');
		ed.undoManager.add();
	},

	insertAndClose : function() {
		var ed = tinyMCEPopup.editor, f = document.forms[0], nl = f.elements, v, args = {}, el;

		tinyMCEPopup.restoreSelection();

		// Fixes crash in Safari
		if (tinymce.isWebKit)
			ed.getWin().focus();

		if (!ed.settings.inline_styles) {
			args = {
				vspace : nl.vspace.value,
				hspace : nl.hspace.value,
				border : nl.border.value,
				align : getSelectValue(f, 'align')
			};
		} else {
			// Remove deprecated values
			args = {
				vspace : '',
				hspace : '',
				border : '',
				align : ''
			};
		}

		tinymce.extend(args, {
			src : nl.media_src.value,
			width : nl.width.value,
			height : nl.height.value,
			alt : nl.alt.value,
			title : nl.title.value,
			'class' : getSelectValue(f, 'class_list'),
			style : nl.style.value,
			id : nl.id.value,
			dir : nl.dir.value,
			lang : nl.lang.value,
			usemap : nl.usemap.value,
			longdesc : nl.longdesc.value
		});

		args.onmouseover = args.onmouseout = '';

		if (f.onmousemovecheck.checked) {
			if (nl.onmouseoversrc.value)
				args.onmouseover = "this.src='" + nl.onmouseoversrc.value + "';";

			if (nl.onmouseoutsrc.value)
				args.onmouseout = "this.src='" + nl.onmouseoutsrc.value + "';";
		}

		el = ed.selection.getNode();

		if (el && el.nodeName == 'IMG') {
			ed.dom.setAttribs(el, args);
		} else {
			ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : 1});
			ed.dom.setAttribs('__mce_tmp', args);
			ed.dom.setAttrib('__mce_tmp', 'id', '');
			ed.undoManager.add();
		}
	},

	getAttrib : function(e, at) {
		var ed = tinyMCEPopup.editor, dom = ed.dom, v, v2;

		if (ed.settings.inline_styles) {
			switch (at) {
				case 'align':
					if (v = dom.getStyle(e, 'float'))
						return v;

					if (v = dom.getStyle(e, 'vertical-align'))
						return v;

					break;

				case 'hspace':
					v = dom.getStyle(e, 'margin-left')
					v2 = dom.getStyle(e, 'margin-right');

					if (v && v == v2)
						return parseInt(v.replace(/[^0-9]/g, ''));

					break;

				case 'vspace':
					v = dom.getStyle(e, 'margin-top')
					v2 = dom.getStyle(e, 'margin-bottom');
					if (v && v == v2)
						return parseInt(v.replace(/[^0-9]/g, ''));

					break;

				case 'border':
					v = 0;

					tinymce.each(['top', 'right', 'bottom', 'left'], function(sv) {
						sv = dom.getStyle(e, 'border-' + sv + '-width');

						// False or not the same as prev
						if (!sv || (sv != v && v !== 0)) {
							v = 0;
							return false;
						}

						if (sv)
							v = sv;
					});

					if (v)
						return parseInt(v.replace(/[^0-9]/g, ''));

					break;
			}
		}

		if (v = dom.getAttrib(e, at))
			return v;

		return '';
	},

	setSwapImage : function(st) {
		var f = document.forms[0];

		f.onmousemovecheck.checked = st;
		setBrowserDisabled('overbrowser', !st);
		setBrowserDisabled('outbrowser', !st);

		if (f.over_list)
			f.over_list.disabled = !st;

		if (f.out_list)
			f.out_list.disabled = !st;

		f.onmouseoversrc.disabled = !st;
		f.onmouseoutsrc.disabled  = !st;
	},

	fillClassList : function(id) {
		var dom = tinyMCEPopup.dom, lst = dom.get(id), v, cl;

		if (v = tinyMCEPopup.getParam('theme_advanced_styles')) {
			cl = [];

			tinymce.each(v.split(';'), function(v) {
				var p = v.split('=');

				cl.push({'title' : p[0], 'class' : p[1]});
			});
		} else
			cl = tinyMCEPopup.editor.dom.getClasses();

		if (cl.length > 0) {
			lst.options.length = 0;
			lst.options[lst.options.length] = new Option(tinyMCEPopup.getLang('not_set'), '');

			tinymce.each(cl, function(o) {
				lst.options[lst.options.length] = new Option(o.title || o['class'], o['class']);
			});
		} else
			dom.remove(dom.getParent(id, 'tr'));
	},

	fillFileList : function(id, l) {
		var dom = tinyMCEPopup.dom, lst = dom.get(id), v, cl;

		l = window[l];
		lst.options.length = 0;

		if (l && l.length > 0) {
			lst.options[lst.options.length] = new Option('', '');

			tinymce.each(l, function(o) {
				lst.options[lst.options.length] = new Option(o[0], o[1]);
			});
		} else
			dom.remove(dom.getParent(id, 'tr'));
	},

	resetImageData : function() {
		var f = document.forms[0];

		f.elements.width.value = f.elements.height.value = '';
	},

	updateImageData : function(img, st) {
		var f = document.forms[0];

		if (!st) {
			f.elements.width.value = img.width;
			f.elements.height.value = img.height;
		}

		this.preloadImg = img;
	},

	changeAppearance : function() {
		var ed = tinyMCEPopup.editor, f = document.forms[0], img = document.getElementById('alignSampleImg');

		if (img) {
			if (ed.getParam('inline_styles')) {
				ed.dom.setAttrib(img, 'style', f.style.value);
			} else {
				img.align = f.align.value;
				img.border = f.border.value;
				img.hspace = f.hspace.value;
				img.vspace = f.vspace.value;
			}
		}
	},

	changeHeight : function() {
		var f = document.forms[0], tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) {
			return;
		}

		if (f.width.value == "" || f.height.value == "")
			return;

		tp = (parseInt(f.width.value) / parseInt(t.preloadImg.width)) * t.preloadImg.height;
		f.height.value = tp.toFixed(0);
	},

	changeWidth : function() {
		var f = document.forms[0], tp, t = this;

		if (!f.constrain.checked || !t.preloadImg) {
			return;
		}

		if (f.width.value == "" || f.height.value == "")
			return;

		tp = (parseInt(f.height.value) / parseInt(t.preloadImg.height)) * t.preloadImg.width;
		f.width.value = tp.toFixed(0);
	},

	updateStyle : function(ty) {
		var dom = tinyMCEPopup.dom, st, v, f = document.forms[0], img = dom.create('img', {style : dom.get('style').value});

		if (tinyMCEPopup.editor.settings.inline_styles) {
			// Handle align
			if (ty == 'align') {
				dom.setStyle(img, 'float', '');
				dom.setStyle(img, 'vertical-align', '');

				v = getSelectValue(f, 'align');
				if (v) {
					if (v == 'left' || v == 'right')
						dom.setStyle(img, 'float', v);
					else
						img.style.verticalAlign = v;
				}
			}

			// Handle border
			if (ty == 'border') {
				dom.setStyle(img, 'border', '');

				v = f.border.value;
				if (v || v == '0') {
					if (v == '0')
						img.style.border = '0';
					else
						img.style.border = v + 'px solid black';
				}
			}

			// Handle hspace
			if (ty == 'hspace') {
				dom.setStyle(img, 'marginLeft', '');
				dom.setStyle(img, 'marginRight', '');

				v = f.hspace.value;
				if (v) {
					img.style.marginLeft = v + 'px';
					img.style.marginRight = v + 'px';
				}
			}

			// Handle vspace
			if (ty == 'vspace') {
				dom.setStyle(img, 'marginTop', '');
				dom.setStyle(img, 'marginBottom', '');

				v = f.vspace.value;
				if (v) {
					img.style.marginTop = v + 'px';
					img.style.marginBottom = v + 'px';
				}
			}

			// Merge
			dom.get('style').value = dom.serializeStyle(dom.parseStyle(img.style.cssText));
		}
	},

	changeMouseMove : function() {
	},

	showPreviewImage : function(u, st) {
		if (!u) {
			tinyMCEPopup.dom.setHTML('prev', '');
			return;
		}

		if (!st && tinyMCEPopup.getParam("stormeimage_update_dimensions_onchange", true))
			this.resetImageData();

		u = tinyMCEPopup.editor.documentBaseURI.toAbsolute(u);

		if (!st)
			tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this);" onerror="ImageDialog.resetImageData();" />');
		else
			tinyMCEPopup.dom.setHTML('prev', '<img id="previewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this, 1);" />');
	}
};

ImageDialog.preInit();
tinyMCEPopup.onInit.add(ImageDialog.init, ImageDialog);
