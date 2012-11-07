function showCoverage(temporal_dynamic) {
    var $temporalCoverageVal = jQuery("#temporalCoverage").val(),
        $infoTemporal = jQuery("#info_temporalCoverage");
    if ($temporalCoverageVal[0] === '-1') {
        $temporalCoverageVal[0] = temporal_dynamic;
    }
    $infoTemporal.html($temporalCoverageVal.reverse().join(', '));
}

function setCoverageInfo(temporal_dynamic) {
    jQuery("#temporalCoverage").change(function () {
        showCoverage(temporal_dynamic);
    });
}

jQuery(document).ready(function($) {
    $("#temporal_btn, #geographical_btn").click(function() {
        var $this = $(this);
        var isTemporal = this.id === 'temporal_btn';
        var $select =  isTemporal ? $this.parent().next() : $this.parent().next().next();
    if($(this).is(":checked") ) {
        $select.val($select[0][0].value).trigger('change');
        $select.find('option:not(":first-child)"').attr('disabled', true);
        if (!isTemporal) {
            $select.prev().hide();
        }
    }
    else { 
        $select.find('option:not(":first-child)"').attr('disabled', false);
        if (!isTemporal) {
            $select.prev().show();
        }
    }
    }); 

    var temporal_dynamic = $("#temporal_dynamic").text(),
        current_temporalCoverage = $("#current_temporalCoverage"),
        info_temporalCoverage = $("#info_temporalCoverage");
    if (current_temporalCoverage.text().indexOf('-1') !== -1) {
        current_temporalCoverage.text(current_temporalCoverage.text().replace('-1', temporal_dynamic));
    }
    if (info_temporalCoverage.text().indexOf('-1') !== -1) {
        info_temporalCoverage.text(info_temporalCoverage.text().replace('-1', temporal_dynamic));
    }

    setCoverageInfo(temporal_dynamic);
});
