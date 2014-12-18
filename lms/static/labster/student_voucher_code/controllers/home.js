angular.module('StudentVoucherCode')

  .controller('HomeController', function ($scope, $location) {
    $scope.voucher_code = "";

    $scope.submit = function() {
      $location.path('/license/new/' + $scope.voucher_code);
    }
  });
