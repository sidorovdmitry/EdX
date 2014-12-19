angular.module('StudentVoucherCode')

  .controller('NewLicenseController', function ($scope, $routeParams, $http) {
    var user_id = window.requestUser.backoffice.user.id;
    $scope.voucher_code = $routeParams.voucher_code;
    $scope.agree_tos = false;
    $scope.payment = [];

    $http.get(url, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        },
        params: {
          'voucher_code': $routeParams.voucher_code,
          'user_id': user_id
        }
      })
        .success(function (data) {
          data.total_in_cent = parseFloat(data.total) * 100;
          data.total = parseFloat(data.total).toFixed(2);
          data.created_date = moment(data.created_at).format('ll');
          $scope.payment = data;
        });

    // $scope.buyLabs = function() {

    // }
  });
