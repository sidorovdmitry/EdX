angular.module('StudentVoucherCode')

  .controller('NewLicenseController', function ($scope, $routeParams) {
    $scope.voucher_code = $routeParams.voucher_code;

    $scope.submit = function() {

    }
  });
