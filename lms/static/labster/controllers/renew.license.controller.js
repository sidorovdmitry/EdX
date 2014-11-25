angular.module('LabsterBackOffice')

  .controller('RenewLicenseController', function ($scope, $http, $routeParams, $location, LicenseService) {
    var licenses_id = $routeParams.licenses_id;
    var user = window.requestUser.backoffice.user.id;
    var url = window.backofficeUrls.get_renew_license_bill;
    $scope.countries = null;
    $scope.totalPrice = 0;
    $scope.tax = 0;
    $scope.vat_error = "";
    $scope.institution_error = "";

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

    $scope.buyLabs = function () {
      $scope.isProcessing = true;
      $scope.checkoutButton = "Processing...";
      if ($scope.institution_type != 1) {
        $scope.vat_error = LicenseService.checkVatFormat($scope.institution_vat_number);
        $scope.institution_error = LicenseService.checkInsitution($scope.institution_name);
      }
      if (!$scope.institution_error.length && !$scope.vat_error.length) {
        var url = window.backofficeUrls.buyLab;
        data = {
          user: window.requestUser.backoffice.user.id,
          is_renew: true,
          payment_type: "manual",
          institution_type : $scope.institution_type,
          institution_name : $scope.institution_name,
          country : $scope.country.id,
          total_before_tax : $scope.subTotalPrice,
          list_product: []
        };

        angular.forEach($scope.license.products, function (lab) {
          if (!lab.is_product_group) {
            // include individual lab
            data.list_product.push({
              product: lab.get_product_id,
              license_id: lab.license_id,
              item_count: lab.item_count,
              month_subscription: lab.month_subscription
            });
          } else {
            // include group package lab
            data.list_product.push({
              product_group: lab.get_product_id,
              license_id: lab.license_id,
              item_count: lab.item_count,
              month_subscription: lab.month_subscription
            });
          }
        });

        $http.post(url, data, {
          headers: {
            'Authorization': "Token " + window.requestUser.backoffice.token
          }
        })
          .success(function (data, status, headers, config) {
            var url = '/invoice/' + data.id;
            $location.url(url);
          })

          .error(function (data, status, headers, config) {
          });
      }
    };  // end of buy lab function
  });