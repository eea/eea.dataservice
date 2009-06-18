jQuery(document).ready(function() { setReferenceTemplatesInKupu(); });

function setReferenceTemplatesInKupu() {
  var kupu_bar = jQuery('#kupu-editor-referenceSystem .kupu-tb-buttons').html();
  jQuery.get('@@getReferenceSystemKupu', {},
    function(data){
      jQuery('#kupu-editor-referenceSystem .kupu-tb-buttons').html(kupu_bar + data);
      jQuery("select[name='reference-system-select']").change(function () { addReferenceSystemTemplate(this) });
    });
};

function addReferenceSystemTemplate(template) {
  jQuery.get('@@getReferenceSystemTemplate', {tpl:jQuery("select[name='reference-system-select']").val()},
    function(data){
      var existing_data = jQuery('#kupu-editor-iframe-referenceSystem').contents().find('body').html();
      jQuery('#kupu-editor-iframe-referenceSystem').contents().find('body').html(data + existing_data);
    });
};
