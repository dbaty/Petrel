// Toggle all checkboxes of a form
function toggleAll(control_checkbox) {
    var new_state = control_checkbox.checked;
    var form = control_checkbox.form;
    for (var i=0; i < form.elements.length; i++) {
        var elm = form.elements[i];
        if (elm.type == "checkbox") {
            elm.checked = new_state;
        }
    }
}

function initHtmlEditor() {
    tinyMCE.init({
        mode: "specific_textareas",
        editor_selector: "html",

        // FIXME: disable some options (or make it configurable)
        theme : "advanced",
        plugins : "pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",

        // FIXME: disable buttons (or make them configurable)
        theme_advanced_buttons1 : "bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,formatselect",
        theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,media,code",
        theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,charmap,iespell,advhr,|,fullscreen",
        theme_advanced_buttons4 : "",
        theme_advanced_toolbar_location : "top",
        theme_advanced_toolbar_align : "left",
        theme_advanced_statusbar_location : "",
        theme_advanced_resizing : true,

        // FIXME
        content_css : "",

        // Drop lists for link/image/media/template dialogs
        // FIXME
        template_external_list_url : "lists/template_list.js",
        external_link_list_url : "lists/link_list.js",
        external_image_list_url : "lists/image_list.js",
        media_external_list_url : "lists/media_list.js"
    });
}