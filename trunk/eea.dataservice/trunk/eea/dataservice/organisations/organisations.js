jQuery(document).ready(function() {

  var overview_detected = $('#organisations-quick-overview');

  if (overview_detected.html()) {
    var organisation = $('#organisations-container li')
    if (organisation.length) {
      jQuery.each(organisation, function(i, value) {
        var org_id = value.id; //#TODO: if ID contains '.' the $('#' + id) will return nothing
        var org_url = $('#' + org_id + '-url').html();

        jQuery.ajax({
          type: "POST",
          url: "/www/SITE/@@migration_link_checker",
          data: "urls:list="+org_url,
          //timeout: 5000,
          dataType: 'json',
          success: function(data){
            var loading_img = $('#' + org_id + '-loading');
            loading_img.css('display', 'none');
            var org_container = $('#' + org_id);
            var msg = data[org_url];
            if (msg == 'Connection timed out' || msg == 'Not Found') {
              msg = '<span style="color: red">Not Found</span>';
            }
            else {
              msg = '<span style="color: green">OK</span>';
            }
            org_container.append(msg);
          }
        });

      });
    }
  }
});
