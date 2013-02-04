/* Show/Hide table definition */
function showDefinition(context) {
    if (jQuery(context).html() === '[+]') {
        jQuery(context).parent().next().css("display","block");
        jQuery(context).html('[x]');
    }
    else {
        jQuery(context).parent().next().css("display","none");
        jQuery(context).html('[+]');
    }
}

function setTableDefShow() {
    jQuery('.table-definition-show').click(function () { showDefinition(this); });
}

jQuery(document).ready(function() {
    setTableDefShow();
    window.DataService.Load();
});

