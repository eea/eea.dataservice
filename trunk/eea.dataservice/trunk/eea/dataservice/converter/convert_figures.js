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
 jQuery.get('FIGURE_ID/@@convertMap');
};

