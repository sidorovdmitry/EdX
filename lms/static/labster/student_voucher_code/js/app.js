angular.module('StudentVoucherCode', ['ngRoute'])

  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: window.baseUrl + 'labster/student_voucher_code/views/home.html'
      })
      .when('/license/new/:voucher_code', {
        controller: 'NewLicenseController',
        templateUrl: window.baseUrl + 'labster/student_voucher_code/views/new_license.html'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
