var conversion_statuses = {
    'completed-status':'Conversion completed',
    'active-status':'Conversion running',
    'pending-status':'Conversion waiting to be processed',
    'error-status':'Conversion did not complete succesful'
};
function convertFigures() {
(function($) {
  var figures = $('#figures-to-convert span');

  if (figures.length) {
    jQuery.each(figures, function(i, value) {
      var figure_url = $(value).attr('rel');
      var label = $('#' + value.id + '-label');
      var image = $('#' + value.id + '-loading');
      var status = $('#' + value.id + '-status');

      jQuery.post(figure_url + '/@@queueConvert', {}, function(data){

        var tid = setInterval(function(){
            jQuery.post(figure_url + '/@@jobStatus', {}, function(data){
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
    });
  }
})(jQuery);
}

jQuery(document).ready(function($) {
  convertFigures();

  $('#checkAll').click(function(){
    var status = $('#checkAll').is(':checked');
    $("INPUT[type='checkbox']").attr('checked', $('#checkAll').is(':checked'));
    $('#checkAll').attr('checked', status);
  });
});
