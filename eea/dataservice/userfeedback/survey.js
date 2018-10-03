var DataService = {'version': '1.0.0'};

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
      link.click(function(){
        return js_context.track(this, '', link.attr('href'));
      });
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
    if(window.ga){
      ga('send', 'pageview', path);
    }
    /* Call Matomo Analytics page traker */
    if(window._paq){
      _paq.push(['setCustomUrl', path]);
      _paq.push(['trackPageView']);
    }
    window.location = next;
    return false;
  }
};

DataService.Load = function(){
  DataService.Google.initialize();
};
