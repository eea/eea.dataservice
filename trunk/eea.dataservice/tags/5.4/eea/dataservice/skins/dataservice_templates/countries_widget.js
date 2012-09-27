// Show/Hide map preview
function showMap() {
  if (jQuery('#map_btn').html() == '[-]') {
    jQuery('#map_canvas').css("display","block");
    jQuery('#map_btn').html('[x]');
  }
  else {
    jQuery('#map_canvas').css("display","none");
    jQuery('#map_btn').html('[-]');
  }
}

function setMapBtn() {
  jQuery('#map_btn').click(function () {
    showMap();
  });
}

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

jQuery(document).ready(function() {
  setMapBtn();
  setWidgetSync();
});
