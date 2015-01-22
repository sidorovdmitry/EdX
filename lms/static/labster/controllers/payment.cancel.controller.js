angular.module('LabsterBackOffice')

  .controller('PaymentCancelController', function ($scope, $filter, $routeParams, $location, $http) {
    $scope.paymentId = $routeParams.paymentId;

    var url = window.backofficeUrls.payment + $scope.paymentId + "/cancel_order/";

    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }})
    .success(function (data, status, headers, config) {
      $scope.allPayments = data.payments;
      $scope.payment = $filter('filter')(data.payments, {id:$scope.paymentId})[0]
    });

    $scope.cancelOrder = function(){
      var post_data = {pk: $scope.paymentId};
      $http.post(url, post_data, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }
      }).success(function (data, status, headers, config) {
        $location.url('/invoice/cancel-order/complete');
      }).error(function (data, status, headers, config) {
      });
    }
  });
