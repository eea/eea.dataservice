var Figures = {version: '1.0.0'};

Figures.fancybox = null;
Figures.jqzoom = null;

Figures.PhotoAlbum = function(content_id){
  content_id = content_id ? content_id : '#region-content';
  this.context = jQuery(content_id);
  this.photos = jQuery('div.photoAlbumEntry', this.context);
  this.photos.removeClass('photoAlbumFolder');

  this.photos.each(function(){
    var photo = jQuery(this);
    var link = jQuery('a', photo);
    var img = jQuery('img', photo);
    var h4 = jQuery('h4', photo.parent());
    var preview = img.attr('src').replace('image_thumb', 'fancybox.html');
    link.attr('href', preview);
    link.attr('rel', h4.attr('id'));
  });

  var js_context = this;
  jQuery('.photoAlbumEntry a').fancybox({
    hideOnContentClick: false,
    frameWidth: 750,
    frameHeight: 450,
    centerOnScroll: false,
    callbackOnShow: js_context.init_zoom,
    callbackOnClose: js_context.close
  });
};

Figures.PhotoAlbum.prototype = {
  init_zoom: function(){
    jQuery(document).trigger('JQ-DEACTIVATE');
    Figures.jqzoom = new Figures.FancyBoxZoom();
  },

  close: function(){
    jQuery(document).trigger('JQ-DEACTIVATE');
  }
};

Figures.FancyBoxZoom = function(){
  this.context = jQuery('#figures-fancyimage');

  var images = jQuery('a.jqzoom', this.context);
  images.css('cursor', 'default');
  images.click(function(){
    return false;
  });

  // Google Analytics
  var tracker = window.pageTracker;
  if(tracker){
    var links = jQuery('a.google-analytics', this.context);
    var path = jQuery('span#google-analytics', this.context).text();
    links.click(function(){
      tracker._trackPageview(path);
    });
  }

  jQuery('a.jqzoom', this.context).jqzoom({
    title: false,
    startOpened: true
  });
};

Figures.FancyBoxZoom.prototype = {
};

Figures.Load = function(){
  Figures.fancybox = new Figures.PhotoAlbum('#region-content');
};
