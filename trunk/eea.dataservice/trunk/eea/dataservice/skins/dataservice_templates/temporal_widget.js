function showCoverage() {
    var $temporalCoverageVal = jQuery("#temporalCoverage").val(),
        $infoTemporal = jQuery("#info_temporalCoverage");
    if ($temporalCoverageVal[0] === '-1') {
        $infoTemporal.html($("#temporal_dynamic").text());
    }
    else {
        $infoTemporal.html($temporalCoverageVal.reverse().join(', '));
    }
}

function setCoverageInfo() {
    jQuery("#temporalCoverage").change(function () {
        showCoverage();
    });
}

jQuery(document).ready(function($) {
    setCoverageInfo();

    $("#temporal_btn, #geographical_btn").toggle(function() {
        var $this = $(this);
        var $select = this.id === 'temporal_btn' ? $this.parent().next() : $this.parent().next().next();
        $select.val($select[0][0].value).trigger('change');
        this.innerHTML = '[x]';
    }, function() {
        this.innerHTML = '[-]';
    });

    var temporal_dynamic = $("#temporal_dynamic").text(),
        current_temporalCoverage = $("#current_temporalCoverage"),
        info_temporalCoverage = $("#info_temporalCoverage");
    if (current_temporalCoverage.text() === '-1') {
        current_temporalCoverage.text(temporal_dynamic);
    }
    if (info_temporalCoverage.text() === '-1') {
        info_temporalCoverage.text(temporal_dynamic);
    }

});
