angular.module('LabsterStudentLicense')

  .controller('NewLicenseController', function ($scope, $routeParams, $http, $timeout) {
    $scope.payment_description = "";

    // get the payment
    var paymentId = $routeParams.paymentId;
    var url = window.backofficeUrls.payment + paymentId + "/";
    $http.get(url, {
      headers: {
        'Authorization': "Token " + window.requestUser.backoffice.token
      }})
    .success(function (data, status, headers, config) {
      data.total_in_cent = parseFloat(data.total) * 100;
      data.total = parseFloat(data.total).toFixed(2);
      data.created_date = moment(data.created_at).format('ll');
      $scope.payment = data;
      checkStripe();
    });

    function setDescription() {
      $scope.payment_description = "Total Payment: ($" + $scope.payment.total + ")";
    }

    function checkStripe() {
      // show stripe form immediately if the user chose to pay with credit card
      if ($scope.payment.payment_type == "stripe") {
        $timeout(function() {
          angular.element('#stripe-button').trigger('click');
        }, 100);
      }
    };
  });
