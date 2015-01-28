angular.module('LabsterBackOffice')

  .controller('PaymentDetailController', function ($scope, $routeParams, $http, ngDialog) {
    $scope.user = window.requestUser;
    $scope.payment = null;
    $scope.show_information = false;

    var paymentId = $routeParams.paymentId;
    var url = window.backofficeUrls.payment + paymentId + "/";

    $scope.pop_up_open = function () {
      ngDialog.open({ template: "invoice_information" });
    };

    $scope.get_invoice = function() {
      var get_invoice_url = window.backofficeUrls.payment + paymentId + "/get_invoice/";
      $http.get(get_invoice_url, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }})
        .success(function(data, status, headers, config){
          // show notification that we have sent an invoice email
          ngDialog.open({ template: "get_invoice" });
        });
    };

    $http.get(url, {
        headers: {
          'Authorization': "Token " + window.requestUser.backoffice.token
        }})
      .success(function (data, status, headers, config) {
        data.total_in_cent = parseFloat(data.total) * 100;
        data.total = parseFloat(data.total).toFixed(2);
        data.created_date = moment(data.created_at).format('ll');
        $scope.payment = data;
      });

    $scope.payment_description = function (payment_products, total) {
      var lab_count = 0;
      var total_license = 0;
      angular.forEach(payment_products, function (product) {
        lab_count++;
        total_license += product.item_count;
      });
      return lab_count + " labs with " + total_license + " licenses. ($" + total + ")";
    };

    $scope.invoiceId = "00" + paymentId;
  });
