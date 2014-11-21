angular.module('LabsterBackOffice')

  .controller('RenewLicenseController', function ($scope, $http, $routeParams, $location, LicenseService) {
    var licenses_id = $routeParams.licenses_id;
    var user = window.requestUser.backoffice.user.id;
    var url = window.backofficeUrls.get_renew_license_bill;
    $scope.countries = null;
    $scope.totalPrice = 0;
    $scope.tax = 0;

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
        $scope.institution_type = data.institution_type;
        $scope.institution_name = data.institution_name;
        $scope.institution_vat_number = data.institution_vat_number;
        $scope.subTotalPrice = parseFloat(data.total_before_tax);
        //$scope.country = data.country;
      });

    // get list of countries
    var url_country = window.backofficeUrls.country;
    $http.get(url_country)
      .success(function (data, status, headers, config) {
        $scope.countries = data;
        $scope.country = $scope.countries[0];
        $scope.checkVat();
//        if ($scope.license != undefined){
//          var idx = $scope.countries.indexOf($scope.license.country);
//          $scope.country = $scope.countries[idx];
//        } else {
//          $scope.country = $scope.countries[0];
//        }
      });

    $scope.checkVat = function () {
      /*
       apply tax if:
       1. Private person within EU
       2. Private institution/school in Denmark
       */
      $scope.totalPrice = 0;
      $scope.tax = 0;
      $scope.is_denmark = false;
      $scope.is_eu_country = LicenseService.checkEuCountry($scope.country);

      if ($scope.country.name == "Denmark") {
        $scope.is_denmark = true;
      }

      if (($scope.is_eu_country && $scope.institution_type == 1) ||
        ( $scope.is_denmark && $scope.institution_type == 2)) {
        $scope.tax = 25 / 100 * $scope.subTotalPrice;
      }

      $scope.totalPrice = $scope.tax + $scope.subTotalPrice;
    };
  });