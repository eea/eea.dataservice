
function showInfo() {
  var countries = jQuery('#geographicCoverage').val();
  jQuery.get('@@getCountriesDisplay', {country_codes:countries}, function(data){
    jQuery('#geo_coverage_info').html(data);
  });
}

function syncCountries() {
  var detect = false;
  var res = [];
  var selectedCountries = jQuery('#geographicCoverage').val();
  selectedCountries = selectedCountries ? selectedCountries: [];

  jQuery.each(groupsData, function(group_id, group_value){
    detect = false;
    jQuery.each(group_value, function(i, val) {
      if (jQuery.inArray(val, selectedCountries) != -1) {
        detect = true;
      }
      else {
        detect = false;
        return false;
      }
    });
    if (detect === true){
      res.push(group_id);
    }
  });

  jQuery('#geographicCoverage_groups').val(res);
  oldGroups = jQuery('#geographicCoverage_groups').val();
  oldGroups = oldGroups ? oldGroups: [];
  showInfo();
}

function syncGroups() {
  var res = [];
  var index = -1;
  var selectedCountries = jQuery('#geographicCoverage').val();
  selectedCountries = selectedCountries ? selectedCountries: [];
  var currentGroups = jQuery('#geographicCoverage_groups').val();
  currentGroups = currentGroups ? currentGroups: [];

  jQuery.each(oldGroups, function(i, val) {
    if (jQuery.inArray(val, currentGroups) == -1) {
      jQuery.each(groupsData[val], function(j, value) {
        index = jQuery.inArray(value, selectedCountries);
        selectedCountries.splice(index,1);
      });
    }
  });

  jQuery.each(currentGroups, function(i, val) {
    jQuery.each(groupsData[val], function(j, value) {
      selectedCountries.push(value);
    });
  });

  jQuery('#geographicCoverage').val(selectedCountries);
  syncCountries();
  oldGroups = jQuery('#geographicCoverage_groups').val();
  oldGroups = oldGroups ? oldGroups: [];
  showInfo();
}

// Synchronize groups and countries
function setWidgetSync() {
  jQuery('#geographicCoverage').change(function () {
    syncCountries();
  });
  jQuery('#geographicCoverage_groups').change(function () {
    syncGroups();
  });
  jQuery.getJSON('@@getCountryGroupsData', {}, function(data){
    oldGroups = [];
    groupsData = data;
    syncCountries();
    oldGroups = jQuery('#geographicCoverage_groups').val();
    oldGroups = oldGroups ? oldGroups: [];
  });
}

// add Dynamic Geotags checkbox on geotags widget in Data and EEAFigure edit form
// TODO: #9423 move this code in a geotags related file
function setDynamicGeotags() {
  jQuery("<p><input type='checkbox' id='dynamic_geotags' />" +
         "<span id='dynamic_geotags_span'>Dynamic Geotags Coverage</span></p>")
        .insertAfter('#location_help');
  jQuery('<span class="formHelp" id="dynamic_geotags_help">' +
         'Warning: Checking this option will remove any previously set geotags</span>')
        .insertAfter("#dynamic_geotags_span");
  var location_edit = jQuery("#location-edit");
  jQuery("#dynamic_geotags").click(function() {
      if(jQuery(this).is(":checked") ) {
          location_edit.attr('disabled', true);
          jQuery("#location-geopreview").prev().text(
            '{"type": "FeatureCollection", "features": [{"geometry":' +
            '{"type": "Point", "coordinates": [0, 0]}, "type": "Feature",' + 
            '"bbox": [], "properties": {"description": "", "tags": "area",' +
            '"country": null, "center": [0, 0], "other": {"name": "Dynamic",' +
            '"geonameId": 6295630, "toponymName": "Dynamic",' +
            '"fclName": "parks,area, ...", "fcode": "AREA", "lat": 0, "lng": 0,' +
            '"fcl": "L", "fcodeName": "area"}, "title": "Dynamic", "name": "6295630"}}]}');
      }
      else { 
          location_edit.attr('disabled', false);
      }
  });

}
jQuery(document).ready(function() {
  setWidgetSync();
  setDynamicGeotags();
});
