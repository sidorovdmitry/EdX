angular.module('StudentVoucherCode')

  .controller('NewLicenseController', function ($scope, $routeParams, $http, $timeout, ngDialog) {
    $scope.user = window.requestUser;
    var user_id = window.requestUser.backoffice.user.id;
    var url = window.backofficeUrls.payment + 'voucher_code/';
    $scope.voucher_code = $routeParams.voucher_code;
//    $scope.agree_tos = false;
    $scope.payment = [];
    $scope.limit_reached = false;

    $scope.payment_description = function (voucher_code, total) {
      return "Voucher " + voucher_code + " with total: ($" + total + ")";
    };

    // update voucher data
    var data = {
      voucher_code: $routeParams.voucher_code,
      user: user_id,
      country: window.requestUser.backoffice.user.country
    };

    $http.post(url, data, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }
    })
      .success(function (data) {
        $scope.payment = data.payment;
        $scope.voucher = data.voucher;
        $scope.limit_reached = data.limit_reached;
        // console.log(data);
        if (data.response_license_id != 0){
          // voucher price is zero, enroll the student
          enrollStudent(data.response_license_id);
        } else {
          checkStripe();
        }
      });

    function checkStripe() {
      // show stripe form immediately if the user chose to pay with credit card
      if ($scope.payment.payment_type == "stripe") {
        $timeout(function() {
          angular.element('#stripe-button').trigger('click');
        }, 100);
      }
    };

    function enrollStudent(license_id) {
      ngDialog.open({
          template: '<h2 class="align-center">Please wait. We are processing your payment.</h2>',
          plain: true,
          showClose: false
      })

      $http.post(
        '/labster/enroll-student/',
        {
          'license_id': license_id,
          'email': $scope.user.email
        },
        {
            headers: {
                'X-CSRFToken': window.csrfToken
            }
        })
        .success(function(data, status, headers, config) {
          ngDialog.close();
          var url = '/student_voucher_code/#/invoice/' + $scope.payment.id + '/thank-you';
          window.location.href = url;
        });
    };
  });
