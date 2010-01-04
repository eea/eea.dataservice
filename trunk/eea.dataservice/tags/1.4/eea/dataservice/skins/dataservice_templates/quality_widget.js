jQuery(document).ready(function() { setQualityMarkers(); setQualityEvents();});

function setQualityEvents() {
    jQuery("#geoQualityCom").change(function () { setQualityMarker('Com') });
    jQuery("#geoQualityLog").change(function () { setQualityMarker('Log') });
    jQuery("#geoQualityPos").change(function () { setQualityMarker('Pos') });
    jQuery("#geoQualityTem").change(function () { setQualityMarker('Tem') });
    jQuery("#geoQualityThe").change(function () { setQualityMarker('The') });
};

function setQualityMarkers() {
    var ids = new Array('Com', 'Log', 'Pos', 'Tem', 'The');
    jQuery.each(ids, function() {
        setQualityMarker(this);
    })
}

function setQualityMarker(ctrl_id) {
    var value = jQuery("#geoQuality"+ctrl_id).val();
    var cells = jQuery(".class-"+"geoQuality"+ctrl_id+" td");

    if (value=='-1') {
        jQuery.each(cells, function() {
            jQuery(this).css({'background-color' : 'red'})
        })
    }
    if (value=='0') {
        jQuery.each(cells, function() {
            jQuery(this).css({'background-color' : 'white'})
        })
    }
    if (value=='1') {
        jQuery.each(cells, function(index, item) {
            if (index=='0') {
                jQuery(this).css({'background-color' : 'LightGreen'})
            }
            else {
                jQuery(this).css({'background-color' : 'white'})
            }
        })
    }
    if (value=='2') {
        jQuery.each(cells, function(index, item) {
            if (index=='2') {
                jQuery(this).css({'background-color' : 'white'})
            }
            else {
                jQuery(this).css({'background-color' : 'LightGreen'})
            }
        })
    }
    if (value=='3') {
        jQuery.each(cells, function() {
            jQuery(this).css({'background-color' : 'LightGreen'})
        })
    }
}
