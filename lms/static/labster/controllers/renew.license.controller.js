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
    $scope.checkoutButton = "Continue to Payment";

    function getLicenseData() {
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
        .success(function (data) {
          $scope.products = data.products;
          $scope.institution_type = data.institution_type;
          $scope.institution_name = data.institution_name;
          $scope.institution_vat_number = data.vat_number;
          $scope.subTotalPrice = parseFloat(data.total_before_tax);
          var idx_country = LicenseService.getIndexCountry(data.country.id, $scope.countries);
          if (idx_country != 0) {
            $scope.country = $scope.countries[idx_country];
          }
          $scope.checkVat();
        });
    }

    // get list of countries
    var url_country = window.backofficeUrls.country;
    $http.get(url_country)
      .success(function (data) {
        $scope.countries = data.countries;
        $scope.countries_vat = data.countries_vat;
        $scope.country = $scope.countries[0];
        getLicenseData();
      });

    $scope.checkVat = function () {
      // call function checkVat() in vat.js
      var vatResult = checkVatHelper($scope.country, $scope.subTotalPrice, $scope.institution_type, $scope.countries_vat);

      $scope.totalPrice = vatResult.totalPrice;
      $scope.tax = vatResult.vat;
    };

    $scope.buyLabs = function () {
      $scope.isProcessing = true;
      if ($scope.institution_type != 1) {
        $scope.vat_error = LicenseService.checkVatFormat($scope.institution_vat_number);
        $scope.institution_error = LicenseService.checkInstitution($scope.institution_name);
      }
      if (!$scope.institution_error.length && !$scope.vat_error.length) {
        $scope.checkoutButton = "Processing...";
        var url = window.backofficeUrls.buyLab;
        data = {
          user: window.requestUser.backoffice.user.id,
          is_renew: true,
          payment_type: "manual",
          institution_type: $scope.institution_type,
          institution_name: $scope.institution_name,
          country: $scope.country.id,
          total_before_tax: $scope.subTotalPrice,
          vat_number: $scope.institution_vat_number,
          list_product: []
        };

        angular.forEach($scope.products, function (lab) {
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
