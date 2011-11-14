var convertFigure = function() {
 jQuery.post('@@convertMap', {cronjob: 1}, function(data){
  var label = $('#convert-label');
  var image = $('#convert-loading');
  var status = $('#convert-status');
  label.html('done');
  label.css('color', 'green');
  image.css('display', 'none');
  status.html('Status: ' + data);
  if (data.charAt(0) == 'S') {
    status.css('color', 'red');
  }
 });
};

jQuery(document).ready(function(){
 convertFigure();
});
