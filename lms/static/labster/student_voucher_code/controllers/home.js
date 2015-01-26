angular.module('StudentVoucherCode')

  .controller('HomeController', function ($scope, $location) {
    $scope.voucher_code = "";

    $scope.submit = function() {
      $location.path('/voucher/' + $scope.voucher_code);
    }
  });
