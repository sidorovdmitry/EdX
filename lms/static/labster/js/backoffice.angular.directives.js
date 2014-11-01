angular.module('LabsterBackOffice')

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
      template: '<button class="button">Credit Card</button>',
      replace: true
    };
  })

  .directive('numeric', function() {
    return {
      require: 'ngModel',
      link: function (scope, element, attr, ngModelCtrl) {
        function fromUser(text) {
          var transformedInput = text.replace(/[^0-9]/g, '');
          if(transformedInput !== text) {
              ngModelCtrl.$setViewValue(transformedInput);
              ngModelCtrl.$render();
          }
          return transformedInput;  // or return Number(transformedInput)
        }
        ngModelCtrl.$parsers.push(fromUser);
      }
    };
  });
