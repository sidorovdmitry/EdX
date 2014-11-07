angular.module('LabsterBackOffice')

  .controller('NewPersonalLicenseController', function ($scope, $routeParams, $location, $http) {
    $scope.labs = [];
    $scope.showLabForm = false;
    $scope.subTotalPrice = 0;
    $scope.tax = 0;
    $scope.totalPrice = 0;
    $scope.isProcessing = false;
    $scope.checkoutButton = "Checkout";
    $scope.is_personal = true;

    $scope.eu_countries = [
      {id:15, name:'Austria'},
      {id:22, name:'Belgium'},
      {id:35, name:'Bulgaria'},

      {id:56, name:'Croatia'},
      {id:59, name:'Cyprus'},
      {id:60, name:'Czech Republic'},
      {id:61, name:'Denmark'},
      {id:70, name:'Estonia'},
      {id:75, name:'Finland'},
      {id:76, name:'France'},
      {id:83, name:'Germany'},
      {id:86, name:'Greece'},
      {id:101, name:'Hungary'},
      {id:107, name:'Ireland'},
      {id:110, name:'Italy'},
      {id:123, name:'Latvia'},
      {id:129, name:'Lithuania'},
      {id:130, name:'Luxembourg'},
      {id:138, name:'Malta'},
      {id:157, name:'Netherlands'},
      {id:177, name:'Poland'},
      {id:178, name:'Portugal'},
      {id:182, name:'Romania'},
      {id:202, name:'Slovakia'},
      {id:203, name:'Slovenia'},
      {id:208, name:'Spain'},
      {id:214, name:'Sweden'},
      {id:234, name:'United Kingdom'},
    ];

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
      $scope.subTotalPrice = $scope.subTotalPrice.toFixed(2);
    };

    $scope.resetCount = function (lab) {
      lab.license = 0;
      lab.total = 0;
      $scope.updateTotal();
    };

    var duplicateLabs = function (list_product, callback) {
      callback();
      return;

      var labs = [],
        post_data;
      angular.forEach(list_product, function (item) {
        labs.push({
          lab_id: item.product,
          license_count: item.item_count
        });
      });

      var post_data = {labs: labs};
      var url = window.backofficeUrls.duplicateLabs;
      $http.post(url, post_data, {
        headers: {
          'Authorization': "Token " + window.requestUser.token
        }
      }).success(function (data, status, headers, config) {
        callback();
      }).error(function (data, status, headers, config) {
      });
    };

    $scope.buyLabs = function () {
      var list_product;

      $scope.isProcessing = true;
      $scope.checkoutButton = "Processing";
      var url = window.backofficeUrls.buyLab;
      data = {
        user: window.requestUser.backoffice.user.id,
        payment_type: "manual",
        list_product: []
      };

      angular.forEach($scope.labs, function (lab) {
        if (lab.license > 0) {
          if (lab.lab_type == "individual") {
            // include individual lab
            data.list_product.push({
              product: lab.id,
              item_count: lab.license,
              month_subscription: lab.month_subscription
            });
          } else {
            // include group package lab
            data.list_product.push({
              product_group: lab.id,
              item_count: lab.license,
              month_subscription: lab.month_subscription
            });
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
          duplicateLabs(list_product, function () {
            var url = '/invoice/' + data.id;
            $location.url(url);
          });
        })

        .error(function (data, status, headers, config) {
        });

    }
  })

  .controller('PaymentListController', function ($scope, $http) {
    $scope.payments = [];

    var url = window.backofficeUrls.payment;
    $http.get(url, {
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