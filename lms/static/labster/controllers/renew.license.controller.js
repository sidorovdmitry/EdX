angular.module('LabsterBackOffice')

  .controller('RenewLicenseController', function ($scope, $http, $routeParams, $location) {
    var licenses_id = $routeParams.licenses_id;
    var user = window.requestUser.backoffice.user.id;
    //var url = window.backofficeUrls.get_renew_license_bill + "?licenses_id=" + licenses_id + "&user_id=" + user;
    var url = window.backofficeUrls.get_renew_license_bill;

    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      },
      params: {
        'licenses_id': licenses_id,
        'user_id': user
      }
    })
    .success(function (data, status, headers, config) {
      $scope.licenses = data;
    });

  });