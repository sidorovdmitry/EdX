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
      .when('/voucher/:voucher_code', {
        controller: 'VoucherController',
        templateUrl: window.baseUrl + 'labster/student_voucher_code/views/voucher_detail.html'
      })
      .when('/invoice/:paymentId/thank-you', {
        controller: 'PaymentPaidController',
        templateUrl: window.baseUrl + 'labster/student_voucher_code/views/payment_paid.html'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
