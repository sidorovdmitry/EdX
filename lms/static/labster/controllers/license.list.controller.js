angular.module('LabsterBackOffice')

  .controller('LicenseListController', function ($scope, $http, $location) {
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

    $scope.selection = "";
    $scope.selection_count = 0;
    // toggle selection for a given employee by name
    $scope.toggleSelection = function toggleSelection(licenseId) {
      var idx = $scope.selection.indexOf(licenseId);

      // is currently selected
      if (idx > -1) {
        $scope.selection = $scope.selection.replace("+" + licenseId, "");
        $scope.selection_count -= 1;
      }

      // is newly selected
      else {
        $scope.selection = $scope.selection + "+" + licenseId;
        $scope.selection_count += 1;
      }
    };

    $scope.renew_license = function() {
      var url = '/renew-license/' + $scope.selection;
      $location.url(url);
    }
  });