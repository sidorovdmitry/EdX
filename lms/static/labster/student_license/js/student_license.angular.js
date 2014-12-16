angular.module('LabsterStudentLicense', ['ngRoute'])

  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        controller: 'HomeController',
        templateUrl: window.baseUrl + 'labster/student_license/view/home.html'
      })
      .otherwise({
        redirectTo: '/'
      });
  })
