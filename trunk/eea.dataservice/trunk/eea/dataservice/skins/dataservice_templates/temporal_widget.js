function showCoverage() {
  jQuery("#info_temporalCoverage").html(jQuery("#temporalCoverage").val().reverse().join(', '));
}

function setCoverageInfo() {
  jQuery("#temporalCoverage").click(function () {
    showCoverage();
  });
}

jQuery(document).ready(function() {
  setCoverageInfo();
});
