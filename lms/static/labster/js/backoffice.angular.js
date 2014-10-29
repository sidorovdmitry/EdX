angular.module('LabsterBackOffice', ['ngRoute'])

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
  })

  .directive('stripe', function ($location, $http) {
    return {
      restrict: 'E',
      scope: {paymentId: '@', email: '@', amount: '@', description: '@'},
      link: function (scope, element, attr) {

        var submitStripe = function (token) {
          var url = window.backofficeUrls.payment + scope.paymentId + "/charge_stripe/";
          var post_data = {
            'stripe_token': token.id
          };

          $http.post(url, post_data, {
            headers: {
              'Authorization': "Token " + window.requestUser.backoffice.token
            }
          })

            .success(function (data, status, headers, config) {
              var url = '/labs/#/invoice/' + scope.paymentId + '/thank-you';
              window.location.href = url;
            })
        };

        var handler = StripeCheckout.configure({
          key: window.stripeKey,
          // image: '/square-image.png',
          token: submitStripe
        });

        element.on('click', function (ev) {
          ev.preventDefault();
          var priceInCent = scope.amount * 100;
          handler.open({
            name: 'Labster',
            description: scope.description,
            amount: priceInCent,
            email: scope.email
          });
        });
      },
      template: '<button class="button">Pay with Credit Card</button>',
      replace: true
    };
  })

  .directive('slideable', function () {
    return {
      restrict: 'C',
      compile: function (element, attr) {
        // wrap tag
        var contents = element.html();
        element.html('<div class="slideable_content" style="margin:0 !important; padding:0 !important" >' + contents + '</div>');

        return function postLink(scope, element, attrs) {
          // default properties
          attrs.duration = (!attrs.duration) ? '1s' : attrs.duration;
          attrs.easing = (!attrs.easing) ? 'ease-in-out' : attrs.easing;
          element.css({
            'overflow': 'hidden',
            'height': '0px',
            'transitionProperty': 'height',
            'transitionDuration': attrs.duration,
            'transitionTimingFunction': attrs.easing
          });
        };
      }
    };
  })
  .directive('slideToggle', function () {
    return {
      restrict: 'A',
      link: function (scope, element, attrs) {
        var target = document.querySelector(attrs.slideToggle);
        attrs.expanded = false;
        element.bind('click', function () {
          var content = target.querySelector('.slideable_content');
          if (!attrs.expanded) {
            content.style.border = '1px solid rgba(0,0,0,0)';
            var y = content.clientHeight;
            content.style.border = 0;
            target.style.height = y + 'px';
          } else {
            target.style.height = '0px';
          }
          attrs.expanded = !attrs.expanded;
        });
      }
    }
  });