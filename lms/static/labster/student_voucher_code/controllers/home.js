angular.module('StudentVoucherCode')

  .controller('HomeController', function ($scope, $location, $http, ngDialog) {
    $scope.voucher_code = "";
    $scope.is_submitting = false;

    $scope.submit = function() {
      var url = window.backofficeUrls.voucher + $scope.voucher_code + "/";
      $scope.is_submitting = true;
      $http.get(url, {
        headers: {
            'Authorization': "Token " + window.requestUser.backoffice.token
        }
      })
      .success(function() {
          $scope.is_submitting = false;
        $location.path('/voucher/' + $scope.voucher_code);
      })
      .error(function() {
        var templates = [
          '<h2>Invalid Voucher Code</h2>',
          '<p>Please ensure that you have copy-pasted the correct voucher (i.e. without quotes or spaces). The voucher code should be 10 characters.</p>',
          '<p>If the code still does not work, please contact your teacher for a valid voucher.</p>',
        ].join("");
        ngDialog.open({
          template: templates,
          plain: true,
          showClose: true
        })
        $scope.is_submitting = false;
      })
    }
  });
