angular.module('LabsterBackOffice')

  .controller('PaymentPaidController', function ($scope, $http, $routeParams) {
    var paymentId = $routeParams.paymentId;
    $scope.payment = {};
    $scope.adwords = "";

    var url = window.backofficeUrls.payment + paymentId + "/";
    $http.get(url, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }})
      .success(function (data, status, headers, config) {
        data.total = parseFloat(data.total).toFixed(2);
        $scope.payment = data;

        // google adwords when user has paid the invoice
        $scope.adwords = '<img height="1" width="1" style="border-style:none;" alt="" src="//www.googleadservices.com/pagead/conversion/982916362/?value=' + $scope.payment.total + '&amp;currency_code=USD&amp;label=k5PiCP_nmVkQirrY1AM&amp;guid=ON&amp;script=0"/>';
      });
  });
