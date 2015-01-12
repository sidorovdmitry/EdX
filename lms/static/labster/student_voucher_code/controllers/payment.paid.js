angular.module('StudentVoucherCode')

  .controller('PaymentPaidController', function ($scope, $routeParams) {
    var paymentId = $routeParams.paymentId;
    $scope.detailUrl = window.backofficeUrls.payment + paymentId;
  });
