angular.module('LabsterBackOffice')

  .controller('NewLicenseController', function ($scope, $routeParams, $location, $http, LicenseService) {
    /*
    $scope.institution_type
    personal = 1
    private = 2
    public = 3
     */
    $scope.labs = [];
    $scope.subTotalPrice = 0;
    $scope.tax = 0;
    $scope.totalPrice = 0;
    $scope.isProcessing = false;
    $scope.showLabForm = true;
    $scope.is_eu_country = false;
    $scope.is_denmark = false;
    $scope.loading = false;
    $scope.institution_vat_number = "";
    $scope.institution_name = "";
    $scope.vat_error = "";
    $scope.institution_error = "";
    $scope.institution_type = 1;
    $scope.institution = "";
    $scope.country = null;
    $scope.default_country = window.requestUser.backoffice.user.country;

    var group_type = $routeParams.group_type;

    $scope.group_type_name = function () {
      if (group_type == 'univ') {
        return 'University & College'
      } else if (group_type == 'hs') {
        return 'High School'
      }
      return "";
    };

    if (group_type != undefined) {
      // load hs and univ packages labs
      var url_group_type = window.backofficeUrls.product_group + '?group_type=' + group_type;

      $http.get(url_group_type, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }
      })

        .success(function (data, status, headers, config) {
          angular.forEach(data, function (lab) {
            lab.license = 0;
            lab.total = 0;
            lab.lab_type = "packages";

            $scope.labs.push(lab);
          });

          // load individual lab
          $scope.load_individual_lab();
        });
    }

    $scope.load_individual_lab = function () {
      var url_individual = window.backofficeUrls.product + '?product_type=' + group_type;
      $http.get(url_individual, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }
      })

        .success(function (data, status, headers, config) {
          angular.forEach(data, function (lab) {
            lab.license = 0;
            lab.total = 0;
            lab.lab_type = "individual";

            $scope.labs.push(lab);
          });
        });
    };

    var url_country = window.backofficeUrls.country;
    $http.get(url_country)
      .success(function (data, status, headers, config) {
        $scope.countries = data;
        $scope.country = $scope.countries[0];
        var idx_country = LicenseService.getIndexCountryByCode($scope.default_country, $scope.countries);
        if (idx_country != 0) {
          $scope.country = $scope.countries[idx_country];
        }
      });

    $scope.updateTotal = function () {
      $scope.subTotalPrice = 0;
      angular.forEach($scope.labs, function (lab) {
        // set default value to 0 if the field is empty
        var length = lab.license.toString().length;
        if (length == 0) {
          lab.license = 0;
        }

        lab.total = lab.license * lab.price;
        $scope.subTotalPrice += lab.total;
        lab.total = lab.total.toFixed(2);

      });
      if ($scope.subTotalPrice > 0) {
        $scope.checkVat();
      }
    };

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

    $scope.resetCount = function (lab) {
      lab.license = 0;
      lab.total = 0;
      $scope.updateTotal();
    };

    var duplicateLabs = function (list_product, payment_id, callback) {
      //callback();
      //return;

      var labs = [],
        post_data;
      angular.forEach(list_product, function (item) {
        angular.forEach(list_product.labster_labs, function (lab_id) {
          labs.push({
            lab_id: lab_id,
            license_count: item.item_count
          });
        });
      });

      var post_data = {labs: labs, payment_id: payment_id, token: window.requestUser.backoffice.token};
      var url = window.backofficeUrls.duplicateLabs;
      $http.post(url, post_data, {
        headers: {
          'Authorization': "Token " + window.requestUser.token
        }
      }).success(function (data, status, headers, config) {
        callback();
      }).error(function (data, status, headers, config) {
      });
    }; // end of duplicateLabs

    $scope.buyLabs = function (payment_method) {
      var list_product;

      $scope.isProcessing = true;
      if ($scope.institution_type != 1) {
        $scope.vat_error = LicenseService.checkVatFormat($scope.institution_vat_number);
        $scope.institution_error = LicenseService.checkInstitution($scope.institution_name);
      } else {
        $scope.vat_error = "";
        $scope.institution_error = "";
      }
      if (!$scope.institution_error.length && !$scope.vat_error.length) {
        // show loading spin
        $scope.loading = true;

        var url = window.backofficeUrls.buyLab;
        data = {
          user: window.requestUser.backoffice.user.id,
          payment_type: payment_method,
          institution_type : $scope.institution_type,
          institution_name : $scope.institution_name,
          country : $scope.country.id,
          total_before_tax : $scope.subTotalPrice,
          vat_number: $scope.institution_vat_number,
          list_product: []
        };

        angular.forEach($scope.labs, function (lab) {
          if (lab.license > 0) {
            if (lab.lab_type == "individual") {
              // include individual lab
              data.list_product.push({
                product: lab.id,
                labster_labs: [lab.external_id],
                item_count: lab.license,
                month_subscription: lab.month_subscription
              });
            } else {
              // include group package lab
              var item = {
                product_group: lab.id,
                labster_labs: [],
                item_count: lab.license,
                month_subscription: lab.month_subscription
              }
              angular.forEach(lab.products, function (each) {
                item.labster_labs.push(each.external_id);
              });
              data.list_product.push(item);
            }
          }
        });

        list_product = data.list_product;
        $http.post(url, data, {
          headers: {
            'Authorization': "Token " + window.requestUser.backoffice.token
          }
        })

          .success(function (data, status, headers, config) {
            duplicateLabs(list_product, data.id, function () {
              var url = '/invoice/' + data.id;
              $location.url(url);
            });
          })

          .error(function (data, status, headers, config) {
          });
      }
    };  // end of buy lab function

    $scope.checkout_btn_class = function () {
      if ($scope.subTotalPrice > 0) {
        return "btn-labster-checkout pull-right";
      } else {
        return "btn-labster-checkout pull-right labster-disabled-btn"
      }
    };

    $scope.showVat = function () {
      $scope.showLabForm = false;
    };

  });
