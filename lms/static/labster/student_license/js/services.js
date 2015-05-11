angular.module('LabsterStudentLicense')

  .factory('StudentLicenseService', function ($http, ngDialog) {
    return({
      enrollStudentApi: enrollStudentApi
    });

    function enrollStudentApi(courseId, paymentId, email) {
      $http.post('/labster/enroll-student-course/',
        {
          'course_id': courseId,
          'email': email
        },
        {
          headers: {
              'X-CSRFToken': window.csrfToken
          }
        })
        .success(function(data, status, headers, config) {
          ngDialog.close();

          var courseId = window.courseId;
          var url = '/student_license/' + courseId + '/#/invoice/' + paymentId + '/thank-you';
          window.location.href = url;

          return true;
          // enrollStudent(courseId, paymentId, email)
        })
        .success(function(data, status, headers, config) {
          return false;
        });
    }

  });
