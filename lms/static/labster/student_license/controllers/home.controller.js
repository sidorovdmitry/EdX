angular.module('LabsterStudentLicense')

  .controller('HomeController', function ($scope, $http) {
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
      }
    }
  });
