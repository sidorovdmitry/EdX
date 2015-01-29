angular.module('LabsterBackOffice', ['ngRoute', 'ngDialog', 'ngAnimate', 'LocalStorageModule'])

  .config(function ($routeProvider, $locationProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: window.baseUrl + 'labster/backoffice/home.html'
      })

      .when('/licenses', {
        controller: 'LicenseListController',
        templateUrl: window.baseUrl + 'labster/backoffice/license_list.html'
      })

      .when('/license/new/group/:group_type', {
        controller: 'NewLicenseController',
        templateUrl: window.baseUrl + 'labster/backoffice/new_license.html'
      })

      .when('/license/new/step2/', {
        controller: 'NewLicenseStep2Controller',
        templateUrl: window.baseUrl + 'labster/backoffice/new_license_step2.html'
      })

      .when('/renew-license/:licenses_id', {
        controller: 'RenewLicenseController',
        templateUrl: window.baseUrl + 'labster/backoffice/renew_license.html'
      })

      .when('/invoice/:paymentId', {
        controller: 'PaymentDetailController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_detail.html'
      })

      .when('/invoice/:paymentId/thank-you', {
        controller: 'PaymentPaidController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_paid.html'
      })

      .when('/invoice/:paymentId/cancel-order', {
        controller: 'PaymentCancelController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_cancel.html'
      })

      .when('/invoice/cancel-order/complete', {
        templateUrl: window.baseUrl + 'labster/backoffice/payment_cancel_finished.html'
      })

      .when('/purchases', {
        controller: 'PaymentListController',
        templateUrl: window.baseUrl + 'labster/backoffice/payment_list.html'
      })

      .otherwise({
        redirectTo: '/'
      });

      // use the HTML5 History API
      $locationProvider.html5Mode({
        enabled: true,
        requireBase: true
      });
  })

// config local storage module
.config(function (localStorageServiceProvider) {
  localStorageServiceProvider
    .setPrefix('LabsterBackOffice');
})

.animation('.slide', function() {
    var NG_HIDE_CLASS = 'ng-hide';
    return {
        beforeAddClass: function(element, className, done) {
            if(className === NG_HIDE_CLASS) {
                element.slideUp(done);
            }
        },
        removeClass: function(element, className, done) {
            if(className === NG_HIDE_CLASS) {
                element.hide().slideDown(done);
            }
        }
    }
});
