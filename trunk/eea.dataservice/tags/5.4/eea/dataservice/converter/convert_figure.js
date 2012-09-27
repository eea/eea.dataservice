var conversion_statuses = {
    'completed-status':'Conversion completed',
    'active-status':'Conversion running',
    'pending-status':'Conversion waiting to be processed',
    'error-status':'Conversion did not complete succesful'
};

var convertFigure = function() {
(function($) {

 jQuery.post('@@queueConvert', {}, function(data){

  var label = $('#convert-label');
  var image = $('#convert-loading');
  var status = $('#convert-status');

        var tid = setInterval(function(){
            jQuery.post('@@jobStatus', {}, function(data){

                if (data in conversion_statuses) {
                    state = conversion_statuses[data];
                } else {
                    state = 'Conversion in unknown state';
                }

                label.html(state);

                if (data == 'completed-status') {
                    label.css('color', 'green');
                    image.css('display', 'none');
                    status.html("");
                    window.clearInterval(tid);
                }

                if (data == 'error-status') {
                    label.css('color', 'red');
                    image.css('display', 'none');
                    status.html("");
                    window.clearInterval(tid);
                }

            });
        }, 1000);

 });
})(jQuery);
};

jQuery(document).ready(function($){
 convertFigure();
});
