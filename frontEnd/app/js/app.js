'use strict';

var App = angular.module('App', ['ngRoute']);

App.factory('myHttpInterceptor', function($rootScope, $q) {
  return {
    'requestError': function(config) {
      $rootScope.status = 'HTTP REQUEST ERROR ' + config;
      return config || $q.when(config);
    },
    'requestError': function(rejection) {
      $rootScope.status = 'HTTP RESPONSE ERROR ' + rejection.status + '\n' +
        rejection.data;
      return $q.reject(rejection);
    },
  };
});

App.factory('switchList', function($rootScope, $http, $q, $log) {
  $rootScope.status = 'Retrieving data...';
  var deferred = $q.defer();
  $http.get('rest/query')
  .success(function(data,status,headers,config) {
    $rootScope.switches = data;
    deferred.resolve();
    $rootScope.status = '';
  });
  return deferred.promise;
});

App.config(function($routeProvider) {
  $routeProvider.when('/', {
    controller  : 'MainCtrl',
    templateUrl : '/partials/main.html',
    resolve     : { 'switchList': 'switchList' },
  });
  $routeProvider.when('/addSwitch', {
    controller  : 'AddCtrl',
    templateUrl : '/partials/insert.html',
  });
  $routeProvider.when('/update/:id', {
    controller  : 'UpdateCtrl',
    templateUrl : '/partials/update.html',
    resolve     : { 'switchList': 'switchList' },
  });
  $routeProvider.otherwise({
    redirectTo  : '/'
  });
});

App.config(function($httpProvider) {
  $httpProvider.interceptors.push('myHttpInterceptor');
});

App.controller('MainCtrl', function($scope, $rootScope, $log, $http, $routeParams, $location, $route) {

  $scope.insert = function() {
    $location.path('/addSwitch');
  };

  $scope.update = function(switch) {
    $location.path('/update/' + switch.id);
  };

  $scope.delete = function(switch) {
    $rootScope.status = 'Deleting switch ' + switch.id + '...';
    $http.post('/rest/delete', {'id': switch.id})
    .success(function(data, status, headers, config) {
      for (var i=0; i<$rootScope.switches.length; i++) {
        if ($rootScope.switches[i].id == switch.id) {
          $rootScope.switches.splice(i, 1);
          break;
        }
      }
      $rootScope.status = '';
    });
  };

});

App.controller('AddCtrl', function($scope, $rootScope, $log, $http, $routeParams, $location, $route) {
  $scope.addSwitch = function() {
    var switch = {
      name: $scope.name,
      id: $scope.id,
    };
    $rootScope.status = 'Creating...';
    $http.post('/rest/insert', switch)
    .success(function(data, status, headers, config) {
      $rootScope.switches.push(data);
      $rootScope.status = '';
    });
    $location.path('/');
  }
});

App.controller('UpdateCtrl', function($routeParams, $rootScope, $scope, $log, $http, $location) {
  for (var i=0, $i<$rootScope.switches.length; i++) {
    if( $rootScope.switches[i].id == $routeParams.id) {
      $scope.switch = angular.copy($rootScope.switches[i]);
  }

  $scope.submitUpdate = function() {
    $rootScope.status = 'Updating...';
    $http.post('/rest/update', $scope.switch)
    .success(function(data, status, headers, config) {
      for(var i=0; i<$rootScope.switches.length; i++) {
        if( $rootScope.switches[i].id == $scope.switches.id) {
          $rootScope.switches.splice(i,1);
          break;
        }
      }
      $rootScope.switches.push(data);
      $rootScope.status = '';
    });
    $location.path('/');
    }
});
