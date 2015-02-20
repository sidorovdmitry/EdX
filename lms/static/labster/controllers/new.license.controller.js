angular.module('LabsterBackOffice')

  .controller('NewLicenseController', function ($scope, $routeParams, $location, $http, localStorageService) {
    /*
    $scope.institution_type
    personal = 1
    private = 2
    public = 3
     */
    $scope.labs = [];
    $scope.subTotalPrice = 0;
    $scope.loading = false;

    var group_type = $routeParams.group_type;

    $scope.group_type_name = function () {
      if (group_type == 'univ') {
        return 'University & College'
      } else if (group_type == 'hs') {
        return 'High School'
      }
      return "";
    };

    // first thing first, load all the labs
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
      // set total price to be the same with subTotalPrice. in the next page we will count the tax and then count the total price
      $scope.totalPrice = $scope.subTotalPrice;
      // if ($scope.subTotalPrice > 0) {
      //   $scope.checkVat();
      // }
    };

    $scope.resetCount = function (lab) {
      lab.license = 0;
      lab.total = 0;
      $scope.updateTotal();
    };

    $scope.checkout_btn_class = function () {
      if ($scope.subTotalPrice > 0) {
        return "btn-labster-checkout pull-right";
      } else {
        return "btn-labster-checkout pull-right labster-disabled-btn"
      }
    };

    $scope.showVatPage = function () {
      // first clear local storage
      localStorageService.remove('paymentStorage');

      // store all data to localStorage and then we will get this in the next page
      $scope.paymentData = {};
      $scope.paymentData.labs = $scope.labs;
      $scope.paymentData.subTotalPrice = $scope.subTotalPrice;
      $scope.paymentData.totalPrice = $scope.totalPrice;

      localStorageService.set('paymentStorage', $scope.paymentData);

      $location.url('/license/new/step2/');
    };

  });
