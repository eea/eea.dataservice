/* Show/Hide table definition */
function showDefinition(context) {
    if (jQuery(context).html() === '[+]') {
        jQuery(context).parent().next().slideDown();
        jQuery(context).html('[x]');
    }
    else {
        jQuery(context).parent().next().slideUp();
        jQuery(context).html('[+]');
    }
}

function setTableDefShow() {
    jQuery('.table-definition-show').click(function () { showDefinition(this); });
}

jQuery(document).ready(function() {
    setTableDefShow();
    if (window.DataService) {
        window.DataService.Load();
    }
});

