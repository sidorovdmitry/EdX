angular.module('LabsterStudentLicense')

  .controller('HomeController', function ($scope, $http, $location) {
    $scope.agree_tos = false;
    $scope.is_submitting = false;
    $scope.btnPayment = "btn-labster-invoice labster-disabled-btn";

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
        console.log(data);
      });

    $scope.updateBtnPayment = function() {
      if($scope.agree_tos) {
        $scope.btnPayment = "btn-labster-invoice";
      } else {
        $scope.btnPayment = "btn-labster-invoice labster-disabled-btn";
      }
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
          country : "",
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
