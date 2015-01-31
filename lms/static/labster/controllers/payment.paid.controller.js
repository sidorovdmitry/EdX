angular.module('LabsterBackOffice')

  .controller('PaymentPaidController', function ($scope, $http, $routeParams) {
    var paymentId = $routeParams.paymentId;
    $scope.payment = {};

    var url = window.backofficeUrls.payment + paymentId + "/";
    $http.get(url, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }})
      .success(function (data, status, headers, config) {
        data.total_in_cent = parseFloat(data.total) * 100;
        data.total = parseFloat(data.total).toFixed(2);
        data.created_date = moment(data.created_at).format('ll');
        $scope.payment = data;
        console.log($scope.payment);
      });

  });
