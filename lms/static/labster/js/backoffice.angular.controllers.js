angular.module('LabsterBackOffice')

  .controller('LicenseListController', function ($scope, $http) {
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
        });

        $scope.licenses = data;
      });

  })

  .controller('NewPersonalLicenseController', function ($scope, $location, $http){
    $scope.labs = [];

    angular.forEach(window.labList, function (lab) {
      lab.license = 0;
      lab.total = 0;

      $scope.labs.push(lab);
    });

    console.log($scope.labs);
  })

  .controller('NewLicenseController', function ($scope, $location, $http) {
    $scope.labs = [];

    angular.forEach(window.labList, function (lab) {
      lab.license = 0;
      lab.total = 0;

      $scope.labs.push(lab);
    });

    $scope.showLabForm = false;
    $scope.totalPrice = 0;
    $scope.isProcessing = false

    $scope.select = function (lab) {
      lab.selected = true;
      $scope.showLabForm = true;
      $scope.updateTotal();
    }

    $scope.deselect = function (lab) {
      lab.selected = false;

      $scope.showLabForm = false;
      angular.forEach($scope.labs, function (lab) {
        if (lab.selected) {
          $scope.showLabForm = true;
          return;
        }
      });

      $scope.updateTotal();
    }

    $scope.selectAll = function () {
      angular.forEach($scope.labs, function (lab) {
        lab.selected = true;
      });

      $scope.showLabForm = true;
      $scope.updateTotal();
    }

    $scope.deselectAll = function () {
      angular.forEach($scope.labs, function (lab) {
        lab.selected = false;
      });

      $scope.showLabForm = false;
      $scope.updateTotal();
    }

    $scope.updateTotal = function () {
      $scope.totalPrice = 0;
      angular.forEach($scope.labs, function (lab) {
        if (lab.selected) {
          lab_license = lab.license;
          if (!lab_license) {
            lab_license = 0;
          }

          lab.total = lab_license * lab.price;
          $scope.totalPrice += lab.total;
          lab.total = lab.total.toFixed(2);
        }
      });
      $scope.totalPrice = $scope.totalPrice.toFixed(2);
    };

    $scope.buyLabs = function () {
      $scope.isProcessing = true;
      var url = window.backofficeUrls.buyLab;
      data = {
        user: window.requestUser.backoffice.user.id,
        payment_type: "manual",
        list_product: []
      };

      angular.forEach($scope.labs, function (lab) {
        if (lab.selected) {
          data.list_product.push({
            product: lab.id,
            item_count: lab.license,
            month_subscription: "6"
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

  })

  .controller('PaymentDetailController', function ($scope, $routeParams, $http) {
    $scope.user = window.requestUser;
    $scope.payment = null;

    var paymentId = $routeParams.paymentId;
    var url = window.backofficeUrls.payment + paymentId;

    $http.get(url)
      .success(function (data, status, headers, config) {
        data.total_in_cent = parseFloat(data.total) * 100;
        data.total = parseFloat(data.total).toFixed(2);
        data.created_date = moment(data.created_at).format('ll');
        $scope.payment = data;
      });

    $scope.invoiceId = "00" + paymentId;
  })

  .controller('PaymentPaidController', function ($scope, $routeParams) {
    var paymentId = $routeParams.paymentId;
    $scope.detailUrl = window.backofficeUrls.payment + paymentId;
  })

  .controller('HomeController', function ($scope) {
  });
