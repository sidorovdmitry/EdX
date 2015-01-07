angular.module('StudentVoucherCode')

  .controller('VoucherController', function ($scope, $location, $http, $routeParams) {
    $scope.voucher_code = $routeParams.voucher_code;

    var url = window.backofficeUrls.voucher + $scope.voucher_code + "/";
    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }})
      .success(function (data, status, headers, config) {
        console.log(data);
      });
  });
