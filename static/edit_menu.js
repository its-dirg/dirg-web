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
    $scope.flatMenuDict = [];

    $scope.typeDropdown = {
        "value": "",
        "values": [
            {
                "type": "public",
                "name": "Public"
            },
            {
                "type": "private",
                "name": "Private"
            },
            {
                "type": "construct",
                "name": "Construct"
            },
            {
                "type": "collapse_close",
                "name": "Collapse close"
            },
            {
                "type": "collapse_open",
                "name": "Collapse open"
            },
            {
                "type": "static",
                "name": "Static"
            }
        ]
    }

    $scope.test = function(){
        alert("test");
    }

    var getMenuFileSuccessCallback = function (data, status) {

        $scope.menuDict = data;

        for (var i = 0; i < data.left.length; i++) {
            var menuItem = data.left[i];
            menuItem['level'] = 1;
            $scope.flatMenuDict.push(menuItem);

            for (var j = 0; j < menuItem['children'].length; j++) {
                var childItem = menuItem['children'][j];
                childItem['level'] = 2;
                $scope.flatMenuDict.push(childItem);

                for (var k = 0; k < childItem['submenu'].length; k++) {
                    var submenuItem = childItem['submenu'][k];
                    submenuItem['level'] = 3;
                    $scope.flatMenuDict.push(submenuItem);

                    for (var l = 0; l < submenuItem['list'].length; l++) {
                        var listItem = submenuItem['list'][l];
                        listItem['level'] = 4;
                        $scope.flatMenuDict.push(listItem);
                    }
                }
            }
        }
    };

    //informationFactory.getFile("menu", getMenuFileSuccessCallback);

    var errorCallback = function (data, status, headers, config) {
        alert(data.ExceptionMessage);
    };

    informationFactory.getFile("menu").success(getMenuFileSuccessCallback).error(errorCallback);

});
