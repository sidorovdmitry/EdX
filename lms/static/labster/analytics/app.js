angular.module('LabsterAnalytics', ['angulartics', 'angulartics.google.tagmanager', 'angulartics.google.analytics'])
    .config(['$locationProvider', function($locationProvider) {
        $locationProvider.html5Mode({enabled: true, requireBase: false});
    }]);
