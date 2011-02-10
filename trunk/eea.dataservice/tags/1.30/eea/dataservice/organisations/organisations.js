function set_url_status(org_id, org_url, update_status,
                        organisations_length, organisations_updated) {

  jQuery.ajax({
    type: "POST",
    url: "/@@migration_link_checker",
    data: "urls:list="+org_url,
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

      //Update status
      if (organisations_updated > update_status.html().split('/')[0]) {
        update_status.html(organisations_updated + '/' + organisations_length);
      }
      if (organisations_updated == organisations_length) {
        var org_loading = $('#organisations-loading');
        org_loading.css('display', 'none');
      }
    }
  });

}

jQuery(document).ready(function() {

  function call_next() {
    pop_and_print();
    if(organisations.length > 0) {
      setTimeout(call_next, 0);
    }
  }

  function pop_and_print() {
    var value = organisations.pop();
    var org_id = value.id;
    var org_url = $('#' + org_id + '-url').html();

    organisations_updated += 1;
    set_url_status(org_id, org_url, update_status,
                   organisations_length, organisations_updated);
  }

  var overview_detected = $('#organisations-quick-overview');

  if (overview_detected.html()) {
    var organisations = jQuery.makeArray($('#organisations-container li'));
    var update_status = $('#org-status-checked');
    var organisations_length = organisations.length;
    var organisations_updated = 0;

    organisations.reverse();
    if (organisations_length) {
      call_next();
    }
  }
});
