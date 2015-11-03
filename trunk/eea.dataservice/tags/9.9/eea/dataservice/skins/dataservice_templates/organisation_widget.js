/* Organisations widget related JS */
/* ------------------------------- */
/*
jQuery(document).ready(function() { setOrganisationInfo(); });

function setOrganisationInfo() {
  var selectors = jQuery('.dummy-org-selector');
  jQuery.each(selectors, function() {
    jQuery("#" + this.id).change(function () { showOrganisationSnippet(this) });
  })
};

function showOrganisationSnippet(context) {
  jQuery.get('@@getOrganisationSnippet', {url:jQuery('#'+ context.id + ' :selected').val()},
    function(data){
      jQuery('#'+ context.id).next().html(data);
      var snippet_container = jQuery('#'+ context.id).next();
      //jQuery(snippet_container).next().html(data);
      jQuery('span', snippet_container).click(function() { clearSnippet(context.id) });
    }
  );
};

function clearSnippet(selector_id) {
  jQuery('#'+ selector_id).next().html('');
}
*/


/* Organisation widget related JS */
/* ------------------------------ */
function clearSnippet(selector_id) {
  jQuery('#'+ selector_id).next().html('');
}

function showOrganisationSnippet(context) {
  jQuery.get('@@getOrganisationSnippet', {url:jQuery('#'+ context.id + ' :selected').val()},
    function(data){
      jQuery('#'+ context.id).next().html(data);
      var snippet_container = jQuery('#'+ context.id).next();
      //jQuery(snippet_container).next().html(data);
      jQuery('span', snippet_container).click(function(){
        clearSnippet(context.id);
      });
    }
  );
}

function setOrganisationInfo() {
  var selectors = jQuery('.dummy-org-selector');
  jQuery.each(selectors, function() {
    jQuery("#" + this.id).change(function(){
      showOrganisationSnippet(this);
    });
  });
}

jQuery(document).ready(function() {
  setOrganisationInfo();
});
