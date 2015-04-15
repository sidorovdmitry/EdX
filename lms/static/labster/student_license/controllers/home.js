angular.module('LabsterStudentLicense')

  .controller('HomeController', function ($scope, $http, $location) {
    $scope.vat = 0;
    $scope.totalPrice = 0;
    $scope.subTotalPrice = 0;
    $scope.agree_tos = false;
    $scope.is_submitting = false;
    $scope.is_eu_country = false;
    $scope.btnPayment = "btn-labster-invoice labster-disabled-btn";
    $scope.default_country = window.country_code;

    var url_product = window.backofficeUrls.product + window.lab_id + '/external_id/';
    $http.get(url_product, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      },
      params: {
        'product_type': window.requestUser.backoffice.user.edu_level,
      }
    })
      .success(function (data, status, headers, config) {
        $scope.lab_info = data;
        $scope.lab_info.item_count = 1;
        $scope.totalPrice = parseFloat($scope.lab_info.price);
        $scope.subTotalPrice = parseFloat($scope.lab_info.price);
      });

    // get list of country
    var url_country = window.backofficeUrls.country;
    $http.get(url_country, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }
    })
      .success(function (data, status, headers, config) {
        $scope.countries = data;
        $scope.country = $scope.countries[0];
        var idx_country = getIndexCountryByCode($scope.default_country, $scope.countries);
        if (idx_country != 0) {
          $scope.country = $scope.countries[idx_country];
        }
      });

    $scope.updateBtnPayment = function() {
      if($scope.agree_tos) {
        $scope.btnPayment = "btn-labster-invoice";
      } else {
        $scope.btnPayment = "btn-labster-invoice labster-disabled-btn";
      }
    };

    $scope.checkVat = function () {
      /*
       apply tax if:
       1. Private person within EU
       2. Private institution/school in Denmark
       */
       // call function checkVat() in vat.js
       var vatResult = checkVatHelper($scope.country, $scope.subTotalPrice, $scope.institution_type);

       $scope.totalPrice = vatResult.totalPrice;
       $scope.vat = vatResult.vat;
    };

    $scope.buyLab = function () {
      if ($scope.agree_tos == true) {
        $scope.is_submitting = true;
        var url = window.backofficeUrls.buyLab;
        data = {
          user: window.requestUser.backoffice.user.id,
          payment_type: "stripe",
          institution_type : 1,
          institution_name : "",
          country : $scope.country.id,
          total_before_tax : $scope.lab_info.price,
          vat_number: 0,
          list_product: []
        };

        var bought_lab = {
          product: $scope.lab_info.id,
          labster_labs: [$scope.lab_info.external_id],
          item_count: 1,
          month_subscription: $scope.lab_info.month_subscription
        };
        data.list_product.push(bought_lab);

        $http.post(url, data, {
          headers: {
            'Authorization': "Token " + window.requestUser.backoffice.token
          }
        })
          .success(function (data, status, headers, config) {
            var url = '/license/new/' + data.id;
            $location.url(url);
          })

          .error(function (data, status, headers, config) {
          });
      }
    };
  });
