angular.module('LabsterBackOffice')

  .controller('LicenseListController', function ($scope, $http) {
    $scope.licenses = [];

    var url = window.backofficeUrls.license;
    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }
    })

      .success(function (data, status, headers, config) {
        angular.forEach(data, function (item) {
          item.end_date = moment(item.date_end_license).format('ll');
          item.date_bought = moment(item.date_bought).format('ll');
        });

        $scope.licenses = data;
      });

    $scope.payments = [];

    // unpaid payment url
    var url_payment = window.backofficeUrls.payment + '?status=0';
    $http.get(url_payment, {
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