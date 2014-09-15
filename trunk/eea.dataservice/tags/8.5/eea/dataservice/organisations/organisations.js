var OrganisationsURLChecker = function(trigger){
  var self = this;

  self.trigger = jQuery(trigger);
  self.loading = jQuery('#organisations-loading');
  self.status = jQuery('#org-status-checked');
  self.context = jQuery('#quick-overview-form');

  self.organisations = jQuery.makeArray(
    jQuery('#organisations-container li', self.context));

  self.organisations.reverse();
  self.total = self.organisations.length;
  self.updated = 0;
};

OrganisationsURLChecker.prototype = {
  run: function(){
    var self = this;
    self.loading.show();
    self.trigger.attr('disabled', true);
    self.next();
  },

  next: function(){
    var self = this;
    self.status.html(self.updated + '/' + self.total);
    if(!self.organisations.length){
      self.loading.hide();
      self.trigger.attr('disabled', false);
      return;
    }

    var value = self.organisations.pop();
    var name = value.id;
    var url = jQuery('#' + name + '-url', self.context).html();

    self.updated += 1;
    self.set_status(name, url);
  },

  set_status: function(name, url) {
    var self = this;
    var query = {"urls:list": url};
    var action = "@@migration_link_checker";
    jQuery.getJSON(action, query, function(data){
      self.handle_response(data, name, url);
      self.next();
    });
  },

  handle_response: function(data, name, url){
    var self = this;
    var output = jQuery('#' + name + '-loading', self.context);

    var msg = data[url];
    if (msg === 'Connection timed out' || msg === 'Not Found') {
      msg = jQuery('<span>').css({color: 'red'}).text('Not Found');
    }
    else {
      msg = jQuery('<span>').css({color: 'green'}).text('OK');
    }
    output.html(msg);
  }
};

var check_organisations_urls = function(trigger) {
  var checker = new OrganisationsURLChecker(trigger);
  checker.run();
};
