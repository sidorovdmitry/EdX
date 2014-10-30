angular.module('LabsterBackOffice', ['ngRoute', 'ngDialog'])

  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: window.baseUrl + 'labster/backoffice/home.html'
      })

      .when('/licenses', {
        controller: 'LicenseListController',
        templateUrl: window.baseUrl + 'labster/backoffice/license_list.html'
      })

      .when('/purchases', {
        controller: 'PaymentListController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_list.html'
      })

      .when('/license/new/personal', {
        controller: 'NewPersonalLicenseController',
        templateUrl: window.baseUrl + 'labster/backoffice/new_personal_license.html'
      })

      .when('/invoice/:paymentId', {
        controller: 'PaymentDetailController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_detail.html'
      })

      .when('/invoice/:paymentId/thank-you', {
        controller: 'PaymentPaidController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_paid.html'
      })

      .otherwise({
        redirectTo: '/'
      });
  });
