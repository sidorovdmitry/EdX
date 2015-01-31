angular.module('StudentVoucherCode')

  .directive('stripe', function ($location, $http, ngDialog) {
    return {
      restrict: 'E',
      scope: {paymentId: '@', email: '@', amount: '@', description: '@', voucherCode: '@'},
      link: function (scope, element, attr) {

        function showProgress() {
          // show progress page while sending data to backoffice api
          ngDialog.open({
              template: '<h2 class="align-center">Please wait. We are processing your payment.</h2>',
              plain: true
          })
        };

        var submitStripe = function (token) {
          showProgress();
          var url = window.backofficeUrls.payment + scope.paymentId + "/charge_stripe/";
          var post_data = {
            'stripe_token': token.id,
            'voucher_code': scope.voucherCode
          };

          $http.post(url, post_data, {
            headers: {
              'Authorization': "Token " + window.requestUser.backoffice.token
            }
          })

            .success(function (data, status, headers, config) {

              // register the student to the course
              // using the license id given
              var license_id = data.license_id;
              $http.post(
                '/labster/enroll-student/',
                {
                  'license_id': license_id,
                  'email': scope.email
                },
                {
                    headers: {
                        'X-CSRFToken': window.csrfToken
                    }
                })
                .success(function(data, status, headers, config) {
                  ngDialog.close();
                  var url = '/student_voucher_code/#/invoice/' + scope.paymentId + '/thank-you';
                  window.location.href = url;
                });
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
      template: '<a class="btn-labster-regular" id="stripe-button"><i class=\'fa fa-credit-card\'></i> &nbsp;&nbsp;Pay with Credit Card</a>',
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
