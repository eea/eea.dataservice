jQuery(document).ready(function() { setCoverageInfo(); });

function setCoverageInfo() {
  jQuery("#temporalCoverage").click(function () { showCoverage() });
};

function showCoverage() {
  jQuery("#info_temporalCoverage").html(jQuery("#temporalCoverage").val().reverse().join(', '));
};
