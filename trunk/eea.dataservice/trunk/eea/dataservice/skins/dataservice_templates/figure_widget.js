var FigureWidget = {version: "1.0.0"};

FigureWidget.Validator = {
  validate: function(input, errors_area, required, integer){
    this.msg = errors_area;
    this.msg.html('');
    input = jQuery(input);
    input.removeClass('figure_input_error');
    var valid = true;
    if(integer){
      valid = valid && this.validate_integer(input);
    }
    if(required){
      valid = valid && this.validate_required(input);
    }
    return valid;
  },

  validate_required: function(input){
    var value = input.val();

    if(!value || value === 0){
      input.addClass('figure_input_error');
      this.msg.html('Value required');
      return false;
    }
    return true;
  },

  validate_integer: function(input){
    var value = input.val();
    value = parseInt(value, 10);
    if(value || value === 0){
      input.val(value);
      return true;
    }else{
      input.addClass('figure_input_error');
      this.msg.html('Value must be integer');
      return false;
    }
  }
};

FigureWidget.Search = {
  initialize: function(){
    this.widgets = jQuery('.figure_widget_right');
    this.widgets.show();

    var js_widget = this;
    this.widgets.each(function(){
      var widget = jQuery(this);
      var input = jQuery('div.figure_widget_search input[type=submit]', widget);
      input.click(function(evt){
        js_widget.submit(input, widget);
        return false;
      });
    });
  },

  submit: function(input, widget){
    var context = this;
    var form = jQuery('.figure_widget_search', widget);
    var eeaid = jQuery('input[type=text]', form);
    var results = jQuery('.figure_widget_results', form);
    var errors_area = jQuery('span.figure_widget_errors', form);
    var nocache = new Date();
    nocache = nocache.getTime();

    // Reset
    results.text('');
    input.removeClass('submitting');

    // Validate
    /* deprecated:
    if(!FigureWidget.Validator.validate(eeaid, errors_area, 1, 1)){
      return false;
    }
    */

    // Submit

    results.text('Searching ...');
    // deprecated: var query = {'eeaid:int': eeaid.val(), nocache: nocache};
    var query = {'title': eeaid.val(), nocache: nocache};
    jQuery.getJSON('@@figure_reference_widget/search', query, function(data){
      if(data.length){
        jQuery.each(data, function(j, result) {
          context.handle_data(result, form, widget);
        });
      }else{
        context.handle_nodata(data, form, widget);
      }
    });
    return false;
  },

  handle_data: function(data, form, widget){
    var results_container = jQuery('.figure_widget_results', form);
    var results = jQuery('.figure_widget_results div.formHelp', form);

    if (results.length === 0) {
      results_container.html('');
      // Help text
      var help = jQuery('<div>');
      help.addClass('formHelp');
      help.text('Click on the following link to insert it as a related EEA product');
      results_container.append(help);}

    // Link
    var link = jQuery('<a>');
    link.html(data.title);
    link.attr('title', data.title);
    link.attr('href', data.url);

    link.click(function(evt){
      var parent = jQuery(widget).parent();
      var select = jQuery('.figure_widget_select', parent);
      var options = jQuery('option', select);
      var already = false;
      options.each(function(){
        var option = jQuery(this);
        if(option.attr('value') == data.uid){
          already = true;
        }
      });
      if(already){
        results_container.html('EEA Product already in list');
      }else{
        var option = jQuery('<option>');
        option.attr('value', data.uid);
        option.attr('selected', 'selected');
        option.html(data.title);
        select.append(option);
        results_container.html('');
      }
      return false;
    });
    results_container.append(link);
    results_container.append('<br />');
  },

  handle_nodata: function(data, form, widget){
    var results = jQuery('.figure_widget_results', form);
    results.html('');
    results.append('<div>No publication found</div>');

    var link = jQuery('<a>');
    link.attr('href', 'publications/createObject?type_name=Report');
    link.attr('title', 'Add new publication');
    link.html('Add it');
    link.click(function(){
      results.html('');
      var new_pub = jQuery('.figure_widget_new_publication', widget);
      var title = jQuery('input[type=text]', form).val();
      //var eeaid = jQuery('input[name=eeaid]', form).val();
      //jQuery('input[name=eeaid]', new_pub).val(eeaid);
      jQuery('input[type=text]', new_pub).val(title);
      new_pub.show();
      form.hide();
      return false;
    });
    results.append(link);
  }
};

FigureWidget.Add = {
  initialize: function(){
    this.widgets = jQuery('.figure_widget_right');

    var js_widget = this;
    this.widgets.each(function(){
      var widget = jQuery(this);
      var form = jQuery('.figure_widget_new_publication', widget);
      var cancel = jQuery('input[name=form.actions.cancel]', form);
      var submit = jQuery('input[name=form.actions.add]', form);
      // Cancel
      cancel.click(function(evt){
        js_widget.cancel(cancel, form, widget);
        return false;
      });

      // Add
      submit.click(function(evt){
        js_widget.add(submit, form, widget);
        return false;
      });
    });
  },

  add: function(input, form, widget){
    input.removeClass('submitting');
    var context = this;
    var title = jQuery('input[type=text]', form);
    // deprecated: var eeaid = jQuery('input[name=eeaid]', form);

    var errors_area = jQuery('.formHelp', title.parent());
    var valid_title = FigureWidget.Validator.validate(title, errors_area, 1, 0);

    /* deprecated:
    errors_area = jQuery('.formHelp', eeaid.parent());
    var valid_eeaid = FigureWidget.Validator.validate(eeaid, errors_area, 1, 1);
    */
    var valid_eeaid = true;

    if(!(valid_title && valid_eeaid)){
      return;
    }

    // deprecated: var query = {title: title.val(), 'eeaid:int': eeaid.val()};
    var query = {title: title.val()};
    jQuery('.figure_widget_new_publication_buttons', form).append('<span>Adding ...</span>');
    jQuery.post('@@figure_reference_widget/add', query, function(data){
      context.handle_data(data, form, widget);
      jQuery('.figure_widget_new_publication_buttons span', form).remove();
    });
  },

  cancel: function(input, form, widget){
    input.removeClass('submitting');
    form.hide();
    jQuery('.figure_widget_search', widget).show();
  },

  handle_data: function(data, form, widget){
    var search = jQuery('.figure_widget_search', widget);
    var results = jQuery('.figure_widget_results', search);
    form.hide();
    results.html(data);
    search.show();
  }
};


jQuery(document).ready(function(){
  FigureWidget.Search.initialize();
  FigureWidget.Add.initialize();
});
