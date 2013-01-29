/* Show/Hide table definition */
jQuery(document).ready(function() {
    setTableDefShow();
    DataService.Load();
});

function setTableDefShow() {
    jQuery('.table-definition-show').click(function () { showDefinition(this) });
}

function showDefinition(context) {
    if (jQuery(context).html() == '[+]') {
        jQuery(context).parent().next().css("display","block");
        jQuery(context).html('[x]');
    }
    else {
        jQuery(context).parent().next().css("display","none");
        jQuery(context).html('[+]');
    }
}
