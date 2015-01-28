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
              var url = '/labs/invoice/' + scope.paymentId + '/thank-you';
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
          var priceInCent = Math.round(scope.amount * 100);

          handler.open({
            name: 'Labster',
            description: scope.description,
            amount: priceInCent,
            email: scope.email
          });
        });
      },
      template: '<a class="btn-labster-regular width-25" id="stripe-button"><i class=\'fa fa-credit-card\'></i> Pay with Credit Card</a>',
      replace: true
    };
  })

  .directive('processing', function () {
    // add spinning icon when clicked
    return function(scope, element, attr) {
      element.on('click', function(ev) {
        $(this).html('<i class=\'fa fa-refresh fa-spin\'></i> Processing');
      });
    }
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
    }

  })

  .directive('selectAll', function() {
    return function(scope, element, attr) {
      element.on('focus', function(ev) {
        $(this)
          .one('mouseup', function () {
            $(this).select();
            return false;
          })
        .select();
      });

      element.on('keyup', function(ev) {
        if ($(this).val() == '0') {
          $(this).select();
        }
      });
    }
  });
