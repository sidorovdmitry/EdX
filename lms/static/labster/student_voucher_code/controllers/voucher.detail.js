angular.module('StudentVoucherCode')

  .controller('VoucherController', function ($scope, $location, $http, $routeParams) {
    $scope.voucher_code = $routeParams.voucher_code;
    $scope.agree_tos = false;
    $scope.btnPayment = "btn-labster-invoice labster-disabled-btn";

    $scope.updateBtnPayment = function() {
      if($scope.agree_tos) {
        $scope.btnPayment = "btn-labster-invoice";
      } else {
        $scope.btnPayment = "btn-labster-invoice labster-disabled-btn";
      }
    };

    $scope.goToPayment = function(){
      if($scope.agree_tos) {
        $location.path('/license/new/' + $scope.voucher_code);
      }
    };

    var url = window.backofficeUrls.voucher + $scope.voucher_code + "/";
    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }})
      .success(function (data, status, headers, config) {
        $scope.voucher = data;
      });
  });
