angular.module('LabsterStudentLicense', ['ngRoute', 'ngDialog'])

  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: window.baseUrl + 'labster/student_license/views/home.html'
      })
      .when('/license/new/:payment_id', {
        controller: 'NewLicenseController',
        templateUrl: window.baseUrl + 'labster/student_license/views/new_license.html'
      })
      .when('/invoice/:paymentId/thank-you', {
        controller: 'PaymentPaidController',
        templateUrl: window.baseUrl + 'labster/student_voucher_code/views/payment_paid.html'
      })
      .otherwise({
        redirectTo: '/'
      });
  })
