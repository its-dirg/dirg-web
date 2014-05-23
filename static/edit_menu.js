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

    $scope.test = function () {
        alert("test");
    }

    $scope.saveMenu = function () {
        alert("Saving menu!");
    }

    $scope.addMenyItem = function (menuItem) {
        var submitId = prompt("Enter a submit id (which is a unique identifier for every page)", "");

        if (submitId != null) {
            var newMenuItem = {
                "name": "",
                "submit": submitId,
                "type": "private"
            }

//            if (menuItem.level == 1) {
//                newMenuItem['class'] = ""
//            } else {
            newMenuItem['parent'] = menuItem['submit']
            newMenuItem['level'] = menuItem['level'] + 1;
//            }

            addElemetToMenuDict(newMenuItem);
        }
    }

    var addElemetToMenuDict = function (newMenuItem) {
        for (var i = 0; i < $scope.flatMenuDict.length; i++) {
            if ($scope.flatMenuDict[i].submit == newMenuItem.parent) {
                $scope.flatMenuDict.splice(i+1, 0, newMenuItem);
                break;
            }
        }
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
                childItem['parent'] = menuItem['submit']
                $scope.flatMenuDict.push(childItem);

                for (var k = 0; k < childItem['submenu'].length; k++) {
                    var submenuItem = childItem['submenu'][k];
                    submenuItem['level'] = 3;
                    submenuItem['parent'] = childItem['submit']
                    $scope.flatMenuDict.push(submenuItem);

                    for (var l = 0; l < submenuItem['list'].length; l++) {
                        var listItem = submenuItem['list'][l];
                        listItem['level'] = 4;
                        listItem['parent'] = submenuItem['submit']
                        $scope.flatMenuDict.push(listItem);
                    }
                    submenuItem['list'] = []
                }
                childItem['submenu'] = []
            }
            menuItem['children'] = []
        }
    };

    //informationFactory.getFile("menu", getMenuFileSuccessCallback);

    var errorCallback = function (data, status, headers, config) {
        alert(data.ExceptionMessage);
    };

    informationFactory.getFile("menu").success(getMenuFileSuccessCallback).error(errorCallback);

});
