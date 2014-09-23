angular.module('LabsterBackOffice', ['ngRoute'])

    .config(function($routeProvider) {
        $routeProvider
            .when('/', {
                controller: 'HomeController',
                templateUrl: window.baseUrl + 'labster/backoffice/home.html'
            })

            .when('/licenses', {
                controller: 'LicenseListController',
                templateUrl: window.baseUrl + 'labster/backoffice/licenses.html'
            })

            .when('/license/new', {
                controller: 'NewLicenseController',
                templateUrl: window.baseUrl + 'labster/backoffice/new_license.html'
            })

            .when('/invoice/:invoiceId', {
                controller: 'InvoiceDetailController',
                templateUrl: window.baseUrl + 'labster/backoffice/invoice_detail.html'
            })

            .otherwise({
                redirectTo: '/'
            });
    })

    .directive('stripe', function() {
        return {
            restrict: 'E',
            scope: {email: '@', amount: '@'},
            link: function(scope, element, attr) {

                var handler = StripeCheckout.configure({
                    key: 'pk_test_mkeBcyfKdPD7qAdTn5zz8vTH',
                    // image: '/square-image.png',
                    token: function(token) {
                        console.dir(token);
                    }
                });

                element.on('click', function(ev) {
                    ev.preventDefault();
                    var priceInCent = scope.amount * 100;
                    var description_text = "2 labs with 10 licenses";
                    handler.open({
                        name: 'Labster',
                        description: description_text,
                        amount: priceInCent,
                        email: scope.email
                    });
                });
            },
            template: '<button class="button">Pay with Stripe</button>',
            replace: true
        };
    })

    .controller('LicenseListController', function($scope) {
        $scope.test_aja = "license list";
    })

    .controller('NewLicenseController', function($scope, $location) {
        $scope.user = window.request_user;
        $scope.labs = [
            {name: "Bacterial Isolation", price: 14.99, license: 0, total: 0},
            {name: "Cytogenetics", price: 14.99, license: 0, total: 0}
        ];
        $scope.showLabForm = false;
        $scope.totalPrice = 0;
        $scope.isProcessing = false

        $scope.select = function(lab) {
            lab.selected = true;
            $scope.showLabForm = true;
            $scope.updateTotal();
        }

        $scope.deselect = function(lab) {
            lab.selected = false;

            $scope.showLabForm = false;
            angular.forEach($scope.labs, function(lab) {
                if (lab.selected) {
                    $scope.showLabForm = true;
                    return;
                }
            });

            $scope.updateTotal();
        }

        $scope.selectAll = function() {
            angular.forEach($scope.labs, function(lab) {
                lab.selected = true;
            });

            $scope.showLabForm = true;
            $scope.updateTotal();
        }

        $scope.deselectAll = function() {
            angular.forEach($scope.labs, function(lab) {
                lab.selected = false;
            });

            $scope.showLabForm = false;
            $scope.updateTotal();
        }

        $scope.updateTotal = function() {
            $scope.totalPrice = 0;
            angular.forEach($scope.labs, function(lab) {
                if (lab.selected) {
                    lab_license = lab.license;
                    if ( ! lab_license) {
                        lab_license = 0;
                    }

                    lab.total = lab_license * lab.price;
                    $scope.totalPrice += lab.total;
                    lab.total = lab.total.toFixed(2);
                }
            });
            $scope.totalPrice = $scope.totalPrice.toFixed(2);
        }

        $scope.buyLabs = function() {
            $scope.isProcessing = true;
            $location.url('/invoice/1')
        }
    })

    .controller('InvoiceDetailController', function($scope, $routeParams) {
        $scope.invoiceId = $routeParams.invoiceId;
        $scope.totalPrice = 299.80;
        $scope.labs = [
            {name: "Bacterial Isolation", price: 14.99, license: 10, total: 149.90},
            {name: "Cytogenetics", price: 14.99, license: 10, total: 149.90}
        ];

        angular.forEach($scope.labs, function(lab) {
            lab.total = lab.total.toFixed(2);
        });

        $scope.totalPrice = $scope.totalPrice.toFixed(2);
    })

    .controller('HomeController', function($scope) {
        $scope.test_aja = "gitu ganti";
    });
