angular.module('LabsterBackOffice', ['ngRoute'])

    .config(function($routeProvider) {
        $routeProvider
            // .when('/', {
            //     controller: 'HomeController',
            //     templateUrl: window.baseUrl + 'labster/backoffice/home.html'
            // })

            .when('/licenses', {
                controller: 'LicenseListController',
                templateUrl: window.baseUrl + 'labster/backoffice/license_list.html'
            })

            .when('/purchases', {
                controller: 'PurchaseListController',
                templateUrl: window.baseUrl + 'labster/backoffice/purchase_list.html'
            })

            .when('/license/new', {
                controller: 'NewLicenseController',
                templateUrl: window.baseUrl + 'labster/backoffice/new_license.html'
            })

            .when('/invoice/:invoiceId', {
                controller: 'InvoiceDetailController',
                templateUrl: window.baseUrl + 'labster/backoffice/invoice_detail.html'
            })

            .when('/invoice/:invoiceId/paid', {
                controller: 'InvoicePaidController',
                templateUrl: window.baseUrl + 'labster/backoffice/invoice_paid.html'
            })

            .otherwise({
                redirectTo: '/licenses'
            });
    })

    .directive('stripe', function($location) {
        return {
            restrict: 'E',
            scope: {email: '@', amount: '@'},
            link: function(scope, element, attr) {

                var handler = StripeCheckout.configure({
                    key: 'pk_test_mkeBcyfKdPD7qAdTn5zz8vTH',
                    // image: '/square-image.png',
                    token: function(token) {
                        window.location.href = '/labs/#/invoice/1/paid/';
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

    .controller('PurchaseListController', function($scope) {
        $scope.invoices = [
            {lab: "Cytogenetics", id: "000001", status: "paid"}
        ];
    })

    .controller('LicenseListController', function($scope) {
        $scope.licenses = [
            {lab: "Cytogenetics", count: 10}
        ];
    })

    .controller('NewLicenseController', function($scope, $location, $http) {
        $scope.labs = [];

        angular.forEach(window.labList, function(lab) {
            lab.license = 0;
            lab.total = 0;

            $scope.labs.push(lab);
        });

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
            var url = window.backofficeUrls.buyLab;
            data = {
                user: window.requestUser.backoffice.user.id,
                payment_type: "manual",
                month_subscription: "6",
                list_product: []
            };

            angular.forEach($scope.labs, function(lab) {
                if (lab.selected) {
                    data.list_product.push({product: lab.id, item_count: lab.license});
                }
            });

            $http.post(url, data, {
                headers: {
                    'Authorization': "Token " + window.requestUser.backoffice.token
                }
            })

            .success(function(data, status, headers, config) {
                console.dir(data);
                var url = '/invoice/' + data.id;
                $location.url(url);
            })

            .error(function(data, status, headers, config) {
            });

        }
    })

    .controller('InvoiceDetailController', function($scope, $routeParams) {
        $scope.user = window.requestUser;
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

    .controller('InvoicePaidController', function($scope) {
        $scope.status = "paid";
    })

    .controller('HomeController', function($scope) {
    });
