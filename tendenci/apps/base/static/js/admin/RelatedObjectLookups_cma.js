// Handles related-objects functionality: lookup link for raw_id_fields
// and Add Another links.

function html_unescape(text) {
    // Unescape a string that was escaped using django.utils.html.escape.
    text = text.replace(/&lt;/g, '<');
    text = text.replace(/&gt;/g, '>');
    text = text.replace(/&quot;/g, '"');
    text = text.replace(/&#39;/g, "'");
    text = text.replace(/&amp;/g, '&');
    return text;
}

// IE doesn't accept periods or dashes in the window name, but the element IDs
// we use to generate popup window names may contain them, therefore we map them
// to allowed characters in a reversible way so that we can locate the correct
// element when the popup window is dismissed.
function id_to_windowname(text) {
    text = text.replace(/\./g, '__dot__');
    text = text.replace(/\-/g, '__dash__');
    return text;
}

function windowname_to_id(text) {
    text = text.replace(/__dot__/g, '.');
    text = text.replace(/__dash__/g, '-');
    return text;
}

function showRelatedObjectLookupPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^lookup_/, '');
    name = id_to_windowname(name);
    var href;
    if (triggeringLink.href.search(/\?/) >= 0) {
        href = triggeringLink.href + '&pop=1';
    } else {
        href = triggeringLink.href + '?pop=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function dismissRelatedLookupPopup(win, chosenId) {
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
        elem.value += ',' + chosenId;
    } else {
        document.getElementById(name).value = chosenId;
    }
    win.close();
}

function showAddAnotherPopup(triggeringLink) {
    var name = triggeringLink.id.replace(/^add_/, '');
    name = id_to_windowname(name);
    href = triggeringLink.href
    if (href.indexOf('?') == -1) {
        href += '?_popup=1';
    } else {
        href  += '&_popup=1';
    }
    var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
    win.focus();
    return false;
}

function dismissAddAnotherPopup(win, newId, newRepr) {
    // newId and newRepr are expected to have previously been escaped by
    // django.utils.html.escape.
    newId = html_unescape(newId);
    newRepr = html_unescape(newRepr);
    var name = windowname_to_id(win.name);
    var elem = document.getElementById(name);
    if (elem) {
        if (elem.nodeName == 'SELECT') {
            var o = new Option(newRepr, newId);
            elem.options[elem.options.length] = o;
            o.selected = true;
			
			// add option to the rest of dropdowns for page and section
			var td_node = elem.parentNode;
			if (td_node !=null) {
				var class_name = td_node.className;
				
				if (class_name !=null && (class_name=='page' || class_name=='section')) {
					var tr_node;
					var c_node;
					var s_node;
				
					tr_node = td_node.parentNode;
					if (tr_node !=null && tr_node.nodeName=='TR') {
					
						// traverse  nextSibling
						var ns = tr_node.nextSibling;
						while (ns !=null && ns.nodeType==1){
							c_node = ns.getElementsByClassName(class_name);
							if (c_node !=null){
								c_node = c_node[0];
								s_node = c_node.getElementsByTagName('select');
								if (s_node !=null){
									s_node = s_node[0]
									o = new Option(newRepr, newId);
									s_node.options[s_node.options.length] = o;
								}
							}
							ns = ns.nextSibling;
						}
						
						// traverse previousSibling
						var ps = tr_node.previousSibling;
						while (ps !=null && ps.nodeType==1){
							c_node = ps.getElementsByClassName(class_name);
							if (c_node !=null){
								c_node = c_node[0];
								s_node = c_node.getElementsByTagName('select');
								if (s_node !=null){
									s_node = s_node[0]
									o = new Option(newRepr, newId);
									s_node.options[s_node.options.length] = o;
								}
							}
							ps = ps.previousSibling;
						}
					}
				}
			}
        } else if (elem.nodeName == 'INPUT') {
            if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
                elem.value += ',' + newId;
            } else {
                elem.value = newId;
            }
        }
    } else {
        var toId = name + "_to";
        elem = document.getElementById(toId);
        var o = new Option(newRepr, newId);
        SelectBox.add_to_cache(toId, o);
        SelectBox.redisplay(toId);
    }
    win.close();
}
