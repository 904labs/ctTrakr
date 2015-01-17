'use strict';

/* Services */

var trakrServices = angular.module('trakrServices', []);

trakrServices.factory('processText', function ($http) {
  return {
    process : function (payload) {
      return $http({
        method  : 'post',
        url     : 'http://localhost:5000/processText',
        params  : {},
        data    : payload
      })
    }
  };
});