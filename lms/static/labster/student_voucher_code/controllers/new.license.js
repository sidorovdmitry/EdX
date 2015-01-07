angular.module('StudentVoucherCode')

  .controller('NewLicenseController', function ($scope, $routeParams, $http) {
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

        console.log(data.payment);
        console.log(data.voucher);
        console.log(data.limit_reached);
      });

    // $scope.buyLabs = function() {

    // }
  });
