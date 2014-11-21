angular.module('LabsterBackOffice')

  .controller('RenewLicenseController', function ($scope, $http, $routeParams, $location, LicenseService) {
    var licenses_id = $routeParams.licenses_id;
    var user = window.requestUser.backoffice.user.id;
    var url = window.backofficeUrls.get_renew_license_bill;
    $scope.countries = null;

    // get license information
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
        $scope.license = data;
        //$scope.country = data.country;
      });

    var url_country = window.backofficeUrls.country;
    $http.get(url_country)
      .success(function (data, status, headers, config) {
        $scope.countries = data;
        $scope.country = $scope.countries[0];
//        if ($scope.license != undefined){
//          var idx = $scope.countries.indexOf($scope.license.country);
//          $scope.country = $scope.countries[idx];
//        } else {
//          $scope.country = $scope.countries[0];
//        }
      });

    $scope.eu_countries = LicenseService.getEuCountries();


  });