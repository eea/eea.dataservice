function showCoverage() {
    jQuery("#info_temporalCoverage").html(jQuery("#temporalCoverage").val().reverse().join(', '));
}

function setCoverageInfo() {
    jQuery("#temporalCoverage").change(function () {
        showCoverage();
    });
}

jQuery(document).ready(function() {
    setCoverageInfo();

    $("#temporal_btn, #geographical_btn").toggle(function() {
        var $this = $(this);
        var $select = this.id === 'temporal_btn' ? $this.parent().next() : $this.parent().next().next();
        var value = this.id === 'temporal_btn' ? '0000' : '00'; 
        if ($select[0][0].innerHTML !== "Dynamic") {
            var opt = $("<option>Dynamic</option>").attr({
                value:value 
            });
            opt.prependTo($select); 
            $select.val(opt.val());
        }
        this.innerHTML = '[x]';
    }, function() {
        this.innerHTML = '[-]';
    });

});
