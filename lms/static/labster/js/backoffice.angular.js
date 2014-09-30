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
                controller: 'PaymentListController',
                templateUrl: window.baseUrl + 'labster/backoffice/payment_list.html'
            })

            .when('/license/new', {
                controller: 'NewLicenseController',
                templateUrl: window.baseUrl + 'labster/backoffice/new_license.html'
            })

            .when('/invoice/:paymentId', {
                controller: 'PaymentDetailController',
                templateUrl: window.baseUrl + 'labster/backoffice/payment_detail.html'
            })

            .when('/invoice/:paymentId/thank-you', {
                controller: 'PaymentPaidController',
                templateUrl: window.baseUrl + 'labster/backoffice/payment_paid.html'
            })

            .otherwise({
                redirectTo: '/licenses'
            });
    })

    .directive('stripe', function($location, $http) {
        return {
            restrict: 'E',
            scope: {paymentId: '@', email: '@', amount: '@'},
            link: function(scope, element, attr) {

                var submitStripe = function(token) {
                    var url = window.backofficeUrls.payment + scope.paymentId + "/charge_stripe/";
                    var post_data = {
                        'stripe_token': token.id
                    }

                    $http.post(url, post_data, {
                        headers: {
                            'Authorization': "Token " + window.requestUser.backoffice.token
                        }
                    })

                    .success(function(data, status, headers, config) {
                        var url = '/labs/#/invoice/' + scope.paymentId + '/thank-you';
                        window.location.href = url;
                    })
                };

                var handler = StripeCheckout.configure({
                    key: window.stripeKey,
                    // image: '/square-image.png',
                    token: submitStripe
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
    });
