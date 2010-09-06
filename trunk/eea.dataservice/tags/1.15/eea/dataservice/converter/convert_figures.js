jQuery(document).ready(function() {
  convertFigures();

  $('#checkAll').click(
    function()
    {
      var status = $('#checkAll').is(':checked');
      $("INPUT[type='checkbox']").attr('checked', $('#checkAll').is(':checked'));
      $('#checkAll').attr('checked', status);
    }
  )
});

function convertFigures() {
  var figures = $('#figures-to-convert span');

  if (figures.length) {
    jQuery.each(figures, function(i, value) {
      jQuery.post(value.id + '/@@convertMap', {cronjob: 1}, function(data){
        var label = $('#' + value.id + '-label');
        var image = $('#' + value.id + '-loading');
        var status = $('#' + value.id + '-status');
        label.html('done');
        label.css('color', 'green');
        image.css('display', 'none');
        status.html('Status: ' + data);
        if (data.charAt(0) == 'S') {
          status.css('color', 'red');
        }
      });
    })
  };
};

