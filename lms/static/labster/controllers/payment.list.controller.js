angular.module('LabsterBackOffice')
  .controller('PaymentListController', function ($scope, $http) {
    $scope.payments = [];

    var url = window.backofficeUrls.payment;
    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }
    })

      .success(function (data, status, headers, config) {
        angular.forEach(data, function (payment) {
          payment.detail_url = '#/invoice/' + payment.id;
          payment.created_date = moment(payment.created_at).format('ll');
        });

        $scope.payments = data;
      });

  });