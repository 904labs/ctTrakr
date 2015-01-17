'use strict';

/* App Module */

var ctTrakrApp = angular.module('ctTrakrApp', [
  'ngRoute',
  'ngAnimate',
  'trakrControllers',
  'trakrServices'
]);

ctTrakrApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
    when('/trakr', {
      templateUrl: 'partials/text-form.html',
      controller: 'trakrCtrl'
    }).
    otherwise({
      redirectTo: '/trakr'
    })
  }
]);
