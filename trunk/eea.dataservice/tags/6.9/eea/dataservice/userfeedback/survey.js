var DataService = {'version': '1.0.0'};

DataService.Survey = {
  initialize: function(context){
    this.context = context ? jQuery('#' + context) : jQuery('#region-content');
    this.links = jQuery('a.feedback-survey', this.context);
    this.selected = null;
    this.cookie = null;
    this.survey_next = {};

    if (!this.links.length){
        return;
    }

    /* Download files */
    var js_context = this;
    this.links.each(function(){
      var link = jQuery(this);
      js_context.survey_next[link.attr('id')] = link.attr('href');
      link.attr('href', '');
      var cookie_id = jQuery('span.google-analytics-path', link).text();
      cookie_id = cookie_id.split('/');
      cookie_id = cookie_id[cookie_id.length-1];
      link.click(function(evt){
        js_context.selected = link;
        js_context.cookie = cookie_id;
        return js_context.open_survey(this);
      });
    });

    /* Dialog */
      this.init_survey();
  },

  init_survey: function(){
    var js_context = this;
    js_context.survey = jQuery('<div>');
    js_context.survey.attr('title', 'Usage feedback');
    jQuery.get('@@survey.html', {}, function(data){
      js_context.survey.html(data);

      /* Init form */
      js_context.init_form();
      js_context.survey.dialog({
        modal: true,
        autoOpen: false,
        width: 800,
        buttons: js_context.buttons()
      });
    });
  },

  init_form: function(){
    var js_context = this;
    var sectors = jQuery('#sectors-widget', js_context.survey);
    var domains = jQuery('#domains-widget', js_context.survey);
    var environment = false;
    var domains_clicked = false;
    var form = jQuery('form', js_context.survey);
    form.submit(function(){
      return false;
    });

    jQuery('input#environment', sectors).click(function(){
      var input = jQuery(this);
      var label = jQuery('label', input.parent());
      if(input.attr('checked')){
        environment = true;
        domains.show();
        label.css('font-weight', 'bold');
      }else{
        environment = false;
        domains.hide();
        label.css('font-weight', 'normal');
        jQuery('input', domains).attr('checked', false);
        domains_clicked = false;
      }
    });

    /* Handle sectors inputs */
    jQuery('input', sectors).click(function(){
      var checked = jQuery('input:checked', sectors);
      if(checked.length){
        if(environment && !domains_clicked){
          js_context.survey.dialog(
            'option', 'buttons', js_context.buttons(false)
          );
        }else{
          js_context.survey.dialog(
            'option', 'buttons', js_context.buttons(true, form)
          );
        }
      }else{
        js_context.survey.dialog(
          'option', 'buttons', js_context.buttons(false)
        );
      }
    });

    /* Handle domains inputs */
    jQuery('input', domains).click(function(){
      var checked = jQuery('input:checked', domains);
      if(checked.length){
        domains_clicked = true;
        js_context.survey.dialog(
          'option', 'buttons', js_context.buttons(true, form)
        );
      }else{
        domains_clicked = false;
        js_context.survey.dialog(
          'option', 'buttons', js_context.buttons(false)
        );
      }
    });
  },

  buttons: function(download, form){
    var js_context = this;
    var res = {};
    if(download){
      res['Download data']= function(){
        js_context.download(form.serialize());
        jQuery(this).dialog('close');
      };
    }

    res.Cancel = function(){
      jQuery(this).dialog('close');
    };

    res.Skip = function(){
      js_context.download('skipped=1');
      jQuery(this).dialog('close');
    };
    return res;
  },

  open_survey: function(link){
    link = jQuery(link);
    var cookie = jQuery.cookie(this.cookie);
    if(!cookie){
      this.survey.dialog('open');
      return false;
    }else{
      return this.download(cookie);
    }
  },

  download: function(query){
    if(!jQuery.cookie(this.cookie)){
      if(query!='skipped=1'){
        jQuery.cookie(this.cookie, query, {expires: 1, path: '/'});
      }
    }

    var next_id = this.selected.attr('id');
    var next = this.survey_next[next_id];
    return DataService.Google.track(this.selected, query, next);
  }
};

DataService.Google = {
  initialize: function(context){
    this.context = context ? jQuery('#' + context) : jQuery('#region-content');
    this.links = jQuery('a.google-analytics', this.context);

    if(!this.links.length){
        return;
    }

    var js_context = this;
    this.links.each(function(){
      var link = jQuery(this);
      if(!link.hasClass('feedback-survey')){
        link.click(function(){
          return js_context.track(this, '', link.attr('href'));
        });
      }
    });
  },

  track: function(link, query, next){
    link = jQuery(link);
    var path = jQuery('span.google-analytics-path', link);
    path = path.text();
    if(query){
      path = path + '?' + query;
    }

    /* Call Google Analytics page traker */
    if(window.pageTracker){
      pageTracker._trackPageview(path);
    }
    window.location = next;
    return false;
  }
};

DataService.Load = function(){
  DataService.Survey.initialize();
  DataService.Google.initialize();
};
