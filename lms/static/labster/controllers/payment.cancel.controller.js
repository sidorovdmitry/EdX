angular.module('LabsterBackOffice')

  .controller('PaymentCancelController', function ($scope, $filter, $routeParams, $location, $http) {
    $scope.batman = "batman";
    $scope.paymentId = $routeParams.paymentId;

    var url = window.backofficeUrls.payment + $scope.paymentId + "/cancel_order/";

    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }})
    .success(function (data, status, headers, config) {
      $scope.payment = data.payment;
      $scope.licenses = data.licenses
      console.log($scope.licenses);
      // $scope.allPayments = data.payments;
      // $scope.payment = $filter('filter')(data.payments, {id:$scope.paymentId})[0]
      // $scope.payment.created_at = moment($scope.payment.created_at).format('ll')
      //console.log($scope.allPayments);
    });

    // var url_license = window.backofficeUrls.license;
    // $http.get(url_license, {
    //   headers: {
    //     'Authorization': "Token " + window.requestUser.backoffice.token
    //   }
    // })

    //   .success(function (data, status, headers, config) {
    //     angular.forEach(data, function (item) {
    //       item.end_date = moment(item.date_end_license).format('ll');
    //       item.date_bought = moment(item.date_bought).format('ll');
    //     });

    //     $scope.licenses = data;
    //     console.log("batman")
    //     console.log(data);
    //   });
  });
