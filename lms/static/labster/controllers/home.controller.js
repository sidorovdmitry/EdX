angular.module('LabsterBackOffice')

  .controller('HomeController', function ($scope) {
    $scope.user_edu_level = window.requestUser.backoffice.user.edu_level;
    $scope.backoffice_user = window.requestUser.backoffice.user;
  });
