var Figures = {version: '1.0.0'};

Figures.fancybox = null;

Figures.PhotoAlbum = function(context){
  this.context = context;
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
    type: 'ajax',
    hideOnContentClick: false,
    width: 870,
    height: 680,
    autoDimensions: false,
    padding: 0,
    margin: 0,
    centerOnScroll: false,
    onComplete: js_context.init_zoom,
    onClosed: js_context.close
  });
};

Figures.PhotoAlbum.prototype = {
  init_zoom: function(){
    jQuery(document).trigger('JQ-DEACTIVATE');
  },

  close: function(){
    jQuery(document).trigger('JQ-DEACTIVATE');
  }
};

Figures.Load = function(){
  var context = jQuery('#region-content');
    Figures.fancybox = new Figures.PhotoAlbum(context);
};
