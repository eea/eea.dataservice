var Figures = {version: '1.0.0'};

Figures.fancybox = null;

Figures.PhotoAlbum = function(context){
  this.context = context;
  this.photos = jQuery('.photoAlbumEntry', this.context);
  this.photos.removeClass('photoAlbumFolder');
  var js_context = this;

  this.photos.each(function(){
    var photo = jQuery(this);
    var link = jQuery('a', photo);
    if ( !link.length || link[0].href.indexOf("data-and-maps/figures") === -1 ) {
        return;
    }

    var href = link.attr('href') + '/fancybox.html';
    link.attr({'href' : href, 'rel': 'fancybox'});
    link.fancybox({
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

jQuery(function($) {
   var tempCoverage = $("#tempCoverage"),
       temporalDynamicText = $("#temporal_dynamic").text(),
       tempCoverageText = tempCoverage.text();
   if(tempCoverage && tempCoverageText === "-1") {
        tempCoverage.text(temporalDynamicText);
   }
});
