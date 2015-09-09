/* EXTERNAL DEPENDENCIES: jquery.fancybox.js */

/*
* Appends fancybox.html url to each photoAlbumEntry link that if found within
* data-and-maps/figures
* eg: http://eea.europa.eu/publications/national-adaptation-policy-processes#tab-figures-used
* */

var Figures = {version: '1.1.0'};

Figures.fancybox = null;

Figures.PhotoAlbum = function(context){
    this.context = context;
    this.photos = jQuery('.photoAlbumEntry', this.context);
    this.photos.removeClass('photoAlbumFolder');
    //var js_context = this;

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
            centerOnScroll: false
            // onComplete: js_context.init_zoom,
            // onClosed: js_context.close
        });
    });

};

// since #9308 we no longer use jqzoom therefere this code will be commented util
// we have another need for onComplete and onClosed functionality
//Figures.PhotoAlbum.prototype = {
//    init_zoom: function(){
//        jQuery(document).trigger('JQ-DEACTIVATE');
//    },
//
//    close: function(){
//        jQuery(document).trigger('JQ-DEACTIVATE');
//    }
//};

Figures.Load = function(){
    var context = jQuery('#region-content');
    Figures.fancybox = new Figures.PhotoAlbum(context);
};

jQuery(function($) {
    /*
     * Show 'Dynamic' instead of -1 for dynamic temporal coverage for Data
     * eg: http://eea.europa.eu/data/european-red-lists-4
     * */
    var tempCoverage = $("#tempCoverage"),
        temporalDynamicText = $("#temporal_dynamic").text(),
        tempCoverageText = tempCoverage.text();
    if(tempCoverage && tempCoverageText === "-1") {
        tempCoverage.text(temporalDynamicText);
    }
    /* #27220 load the figure fancybox transform only if we have relatedItems since we only use
       this functionality there */
    if ($("#relatedItems").length) {
        Figures.load();
    }
});
