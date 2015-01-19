angular.module('LabsterBackOffice')

  .controller('PaymentCancelController', function ($scope, $routeParams, $location, $http) {
    $scope.batman = "batman";
    $scope.userId = $routeParams.userId;
    $scope.paymentId = $routeParams.paymentId;
  });
