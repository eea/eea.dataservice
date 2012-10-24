function showCoverage() {
    var $temporalCoverageVal = jQuery("#temporalCoverage").val(),
        $infoTemporal = jQuery("#info_temporalCoverage");
    if ($temporalCoverageVal[0] === '0000') {
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
        var value = this.id === 'temporal_btn' ? '0000' : '00'; 
        var opt = $("<option>Dynamic</option>").attr({
            value:value 
        });
        if ($select[0][0].innerHTML !== "Dynamic") {
            opt.prependTo($select); 
        }
        $select.val(opt.val()).trigger('change');
        this.innerHTML = '[x]';
    }, function() {
        this.innerHTML = '[-]';
    });

});
