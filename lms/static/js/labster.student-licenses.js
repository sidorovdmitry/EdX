_.templateSettings = {
    interpolate: /\{\{(.+?)\}\}/g
};

function postEnrollProcess(data) {
  var emails = [],
      newList = [],
      currentEmails = [];

  _.each(data.results, function(result) {
      emails.push(result.identifier);
  });

  if (data.action == "enroll") {
    _.each(window.userLicenses, function(license) {
        currentEmails.push(license.email);
    });

    _.each(emails, function(email) {
        if (_.contains(currentEmails, email) === false) {
          window.userLicenses.push({email: email});
        }
    });

  } else if (data.action == "unenroll") {
    _.each(window.userLicenses, function(license) {
        if (_.contains(emails, license.email) === false) {
          newList.push(license);
        }
    });

    window.userLicenses = newList;
  }

  updateLicenseList();
}

function revokeMembership(ev) {
  var el = $(ev.currentTarget),
      email;

  el.empty().append('<i class="icon fa fa-spinner fa-spin"></i> Processing &hellip;');
  email = el.data('email');

  $.ajax({
    type: 'POST',
    url: '/courses/' + window.courseId + '/instructor/api/students_update_enrollment',
    data: {
      action: "unenroll",
      auto_enroll: true,
      email_students: true,
      identifiers: email
    },
    success: function(data) {
      el.parents('tr').remove();
    },
    error: function() {
    }
  });
}

function updateLicenseList() {
  var container = $('.student-license-container'),
      tbody = container.find('tbody'),
      template = _.template($('#license-row-template').html());

  tbody.empty();
  _.each(window.userLicenses, function(license) {
      var rendered = template(license),
          rendered_el;
      rendered_el = $(rendered);
      rendered_el.find('.revoke').click(revokeMembership);
      tbody.append(rendered_el);
  });
}
(function() { updateLicenseList(); })();

