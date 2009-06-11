FacetedEdit.SelectWidget = function(wid){
  this.wid = wid;
  this.widget = jQuery('#' + wid + '_widget');
  this.elements = jQuery('option', this.widget);
  this.select = jQuery('#' + this.wid);
  var value = this.select.val();
  this.selected = jQuery('option[value='+ value +']', this.widget);

  // Handle change
  var js_widget = this;
  this.select.change(function(evt){
    js_widget.set_default(this);
  });
};

FacetedEdit.SelectWidget.prototype = {
  set_default: function(element){
    var value = this.select.val();
    this.selected = jQuery('option[value='+ value +']', this.widget);

    var query = {};
    query.redirect = '';
    query.updateCriterion_button = 'Save';
    query.cid = this.wid;
    query[this.wid + '_default'] = value;

    jQuery.post('@@faceted_configure', query, function(data){
      FacetedEdit.FormMessage.update(data);
    });
  }
};

var initializeSelectWidget = function(){
  jQuery('div.faceted-select-widget').each(function(){
      var wid = jQuery(this).attr('id');
      wid = wid.split('_')[0];
      FacetedEdit.Widgets[wid] = new FacetedEdit.SelectWidget(wid);
  });
};

jQuery(document).ready(function(){
  jQuery(FacetedEdit.Events).bind(
    FacetedEdit.Events.INITIALIZE_WIDGETS,
    initializeSelectWidget
  );
});
