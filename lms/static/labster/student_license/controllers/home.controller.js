angular.module('LabsterStudentLicense')

  .controller('HomeController', function ($scope, $http) {
    $scope.agree_tos = false;

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

    $scope.buyLab = function () {

    }
  });
