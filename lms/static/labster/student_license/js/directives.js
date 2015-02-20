angular.module('LabsterStudentLicense')

  .directive('stripe', function ($location, $http, ngDialog) {
    return {
      restrict: 'E',
      scope: {paymentId: '@', email: '@', amount: '@', description: '@', courseId: '@'},
      link: function (scope, element, attr) {

        function showProgress() {
          // show progress page while sending data to backoffice api
          ngDialog.open({
              template: '<h2 class="align-center">Please wait. We are processing your payment.</h2>',
              plain: true,
              showClose: false,
              closeByDocument: false,
              closeByEscape : false
          })
        };

        var submitStripe = function (token) {
          showProgress();
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

              // register the student to the course
              $http.post(
                '/labster/enroll-student-course/',
                {
                  'course_id': scope.courseId,
                  'email': scope.email
                },
                {
                    headers: {
                        'X-CSRFToken': window.csrfToken
                    }
                })
                .success(function(data, status, headers, config) {
                  var courseId = window.courseId;
                  ngDialog.close();
                  var url = '/student_license/' + courseId + '/#/invoice/' + scope.paymentId + '/thank-you';
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
  });
