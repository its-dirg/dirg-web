var app = angular.module("editMenuApp", [])

app.factory('informationFactory', function ($http) {
    return {
        getFile: function (name) {
            return $http.get("/file?name=" + name);
        }
    }
});

app.controller("HelloController", function ($scope, informationFactory) {

    $scope.menuDict;

    var getMenuFileSuccessCallback = function (data, status) {
        $scope.menuDict = data;
    };

    //informationFactory.getFile("menu", getMenuFileSuccessCallback);

    var errorCallback = function (data, status, headers, config) {
        alert(data.ExceptionMessage);
    };

    informationFactory.getFile("menu").success(getMenuFileSuccessCallback).error(errorCallback);

});
