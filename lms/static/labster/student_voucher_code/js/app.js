angular.module('StudentVoucherCode', ['ngRoute'])

  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: window.baseUrl + 'labster/student_voucher_code/views/home.html'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
