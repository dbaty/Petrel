// Toggle all checkboxes of a form
function toggleAll(control_checkbox) {
    var new_state = control_checkbox.checked;
    var form = control_checkbox.form;
    for (var i=0; i < form.elements.length; i++) {
        var elm = form.elements[i];
        if (elm.type == 'checkbox') {
            elm.checked = new_state;
        }
    }
}