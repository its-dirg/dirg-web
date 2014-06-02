var app = angular.module("editMenuApp", [])

app.factory('informationFactory', function ($http) {
    return {
        getFile: function (name) {
            return $http.get("/file?name=" + name);
        },

        postLeftMenu: function (leftMenu) {
            return $http.post("/post_left_menu", {"leftMenu": leftMenu});
        }
    }
});

app.controller("HelloController", function ($scope, informationFactory) {

    $scope.menuDict;
    $scope.flatMenuDict = [];

    $scope.headerVisibility = {
        "value": "",
        "values": [
            {
                "type": "static",
                "name": "Static"
            },
            {
                "type": "collapse_close",
                "name": "Collapse close"
            },
            {
                "type": "collapse_open",
                "name": "Collapse open"
            }
        ]
    }

    $scope.menuItemVisibility = {
        "value": "",
        "values": [
            {
                "type": "construct",
                "name": "Construct"
            },
            {
                "type": "public",
                "name": "Public"
            },
            {
                "type": "private",
                "name": "Private"
            }
        ]
    }

    $scope.modalWindowsInformation = {
        "menuItemRealtionDropDown": {
            "value": "sibling",
            "values": [
                {
                    "type": "sibling",
                    "name": "Root item"
                },
                {
                    "type": "child",
                    "name": "Drop-down item"
                },
                {
                    "type": "header",
                    "name": "Page header"
                },
                {
                    "type": "submenu",
                    "name": "Page submenu"
                }
            ]
        },
        "submitId": ""
    }

    $scope.test = function () {
        alert("test");
    }

    var originalMenuDict = []

    var convertToOriginalMenuStructure = function () {
        for (var i = 0; i < $scope.flatMenuDict.length; i++) {
            //var currentMenuItem = $scope.flatMenuDict[i];
            var currentMenuItem = jQuery.extend(true, {}, $scope.flatMenuDict[i]);

            if (currentMenuItem.level == 1) {
                currentMenuItem['children'] = []
                originalMenuDict.push(currentMenuItem)
            }
            else if (currentMenuItem.level == 2) {
                addSecondLevelMenuToParent(currentMenuItem)
            }
            else if (currentMenuItem.level == 3) {
                addThirdLevelMenuToParent(currentMenuItem)
            }
            else if (currentMenuItem.level == 4) {
                addForthLevelMenuToParent(currentMenuItem)
            }
        }

        console.log(originalMenuDict)
    }

    var addDropDownAttribute = function () {
        for (var j = 0; j < $scope.flatMenuDict.length; j++) {
            if ($scope.flatMenuDict[j].level == 1) {
                if ($scope.flatMenuDict[j].children.length > 0) {
                    $scope.flatMenuDict[j]['class'] = "dropdown"
                }
            }
        }
    }

    var removeUnusedAttributes = function () {
        for (var i = 0; i < originalMenuDict.length; i++) {
            delete originalMenuDict[i]["level"];
            delete originalMenuDict[i]["menuType"]
            var levelTwoMenuItems = originalMenuDict[i].children;

            for (var j = 0; j < levelTwoMenuItems.length; j++) {
                delete levelTwoMenuItems[j]["level"];
                delete levelTwoMenuItems[j]["parent"];
                delete originalMenuDict[i]["menuType"]
                var levelThreeMenuItems = originalMenuDict[i].children[j].submenu;

                for (var k = 0; k < levelThreeMenuItems.length; k++) {
                    delete levelThreeMenuItems[k]["level"];
                    delete levelThreeMenuItems[k]["parent"];
                    delete originalMenuDict[i]["menuType"]
                    var levelFourMenuItems = originalMenuDict[i].children[j].submenu[k].list;

                    for (var l = 0; l < levelFourMenuItems.length; l++) {
                        delete levelFourMenuItems[l]["level"];
                        delete levelFourMenuItems[l]["parent"];
                        delete originalMenuDict[i]["menuType"]
                    }
                }
            }
        }
    }

    var getPostMenuSuccessCallback = function (data, status) {
        console.log("getMenuFileSuccessCallback")
    }


    $scope.saveMenu = function () {

        //Switch the menu back so that level 1 contains sub menu and so on
        convertToOriginalMenuStructure();

        //Add the dropdown attribute to the level 1 menu items it the are any children
        addDropDownAttribute();

        removeUnusedAttributes();

        informationFactory.postLeftMenu(originalMenuDict).success(getPostMenuSuccessCallback).error(errorCallback);
    }

    var addSecondLevelMenuToParent = function (menuItem) {
        menuItemTypes = $scope.modalWindowsInformation.menuItemRealtionDropDown.values;

        for (var i = 0; i < originalMenuDict.length; i++) {
            if (originalMenuDict[i].submit == menuItem.parent) {
                var parentMenuItem = jQuery.extend(true, {}, originalMenuDict[i]);

                if (menuItem.menuType.type == menuItemTypes[1].type) {
                    parentMenuItem['children'].push(menuItem)
                }
                else if (menuItem.menuType == menuItemTypes[2]) {
                    parentMenuItem['submenu'].push(menuItem)
                }

                originalMenuDict[i] = parentMenuItem;
                break;
            }
        }
    }

    var addThirdLevelMenuToParent = function (menuItem) {
        for (var i = 0; i < originalMenuDict.length; i++) {
            for (var j = 0; j < originalMenuDict[i].children.length; j++) {
                //thirdLevelMenuDict = originalMenuDict[i].children[j];
                var thirdLevelMenuDict = jQuery.extend(true, {}, originalMenuDict[i].children[j]);
                if (thirdLevelMenuDict.submit == menuItem.parent) {
                    thirdLevelMenuDict['submenu'].push(menuItem)
                    originalMenuDict[i].children[j] = thirdLevelMenuDict;
                    break;
                }
            }
        }
    }

    var addForthLevelMenuToParent = function (menuItem) {
        for (var i = 0; i < originalMenuDict.length; i++) {
            for (var j = 0; j < originalMenuDict[i].children.length; j++) {
                for (var k = 0; k < originalMenuDict[i].children[j].submenu.length; k++) {
                    //thirdLevelMenuDict = originalMenuDict[i].children[j].submenu[k];
                    var thirdLevelMenuDict = jQuery.extend(true, {}, originalMenuDict[i].children[j].submenu[k]);

                    if (thirdLevelMenuDict.submit == menuItem.parent) {
                        thirdLevelMenuDict['list'].push(menuItem)
                        originalMenuDict[i].children[j].submenu[k] = thirdLevelMenuDict;
                        break;
                    }
                }
            }
        }
    }

    $scope.deleteMenuItem = function (menuItem) {
        var childrenAndSubChildrenIndexes = getChildrenIndexs(menuItem);
        var selectedMenuItemIndex = getMenuItemIndex(menuItem);

        var shouldDeleteMenuItem = window.confirm("Do you really want to remove this item?");

        if (shouldDeleteMenuItem == true)
            deleteMenuItem(selectedMenuItemIndex, childrenAndSubChildrenIndexes);
    }

    var getChildrenIndexs = function (menuItem) {
        var childrenIndexList = []
        for (var index = 0; index < $scope.flatMenuDict.length; index++) {
            if ($scope.flatMenuDict[index].level > menuItem.level) {
                if (menuItem.submit == $scope.flatMenuDict[index].parent) {
                    subChildrenIndexList = getChildrenIndexs($scope.flatMenuDict[index])
                    childrenIndexList.push(index)
                    childrenIndexList = childrenIndexList.concat(subChildrenIndexList)
                }
            }
        }
        return childrenIndexList;
    }

    var deleteMenuItem = function (selectedMenuItemIndex, childrenAndSubChildrenIndexes) {
        $scope.flatMenuDict.splice(selectedMenuItemIndex, childrenAndSubChildrenIndexes.length + 1);
    }

    $scope.selectedMenuItem;

    $scope.showNewMenuItemModalWindow = function (menuItem) {
        var menuItemRelationList = $scope.modalWindowsInformation.menuItemRealtionDropDown.values;
//
//        if (menuItem.menuType == menuItemRelationList[0]) {
//            $scope.modalWindowsInformation = {
//                "menuItemRealtionDropDown": {
//                    "value": "sibling",
//                    "values": [
//                        {
//                            "type": "sibling",
//                            "name": "Root item"
//                        },
//                        {
//                            "type": "child",
//                            "name": "Drop-down item"
//                        },
//                        {
//                            "type": "header",
//                            "name": "Page header"
//                        }
//                    ]
//                },
//                "submitId": ""
//            }
//        }
//        else if (menuItem.menuType == menuItemRelationList[1]) {
//            $scope.modalWindowsInformation = {
//                "menuItemRealtionDropDown": {
//                    "value": "child",
//                    "values": [
//                        {
//                            "type": "child",
//                            "name": "Drop-down item"
//                        },
//                        {
//                            "type": "header",
//                            "name": "Page header"
//                        }
//                    ]
//                },
//                "submitId": ""
//            }
//        }
//        else if (menuItem.menuType == menuItemRelationList[2]) {
//            $scope.modalWindowsInformation = {
//                "menuItemRealtionDropDown": {
//                    "value": "header",
//                    "values": [
//                        {
//                            "type": "header",
//                            "name": "Page header"
//                        },
//                        {
//                            "type": "submenu",
//                            "name": "Page submenu"
//                        }
//                    ]
//                },
//                "submitId": ""
//            }
//        }


        $('#newMenuItemModalWindow').modal('show');
        $scope.selectedMenuItem = menuItem;
    }

    $scope.errorMessage = ""

    $scope.submitNewMenuItemModalWindow = function () {
        $scope.errorMessage = ""
        var selectedMenuItem = $scope.selectedMenuItem;
        var menuItemRelation = $scope.modalWindowsInformation.menuItemRealtionDropDown.value;
        var menuItemRelationList = $scope.modalWindowsInformation.menuItemRealtionDropDown.values;
        var submitId = $scope.modalWindowsInformation.submitId;

        if (submitId != null) {
            for (var i = 0; i < $scope.flatMenuDict.length; i++) {
                if (submitId == $scope.flatMenuDict[i].submit) {
                    $scope.errorMessage = "The submit id you entered is not unique"
                    return
                }
                else if (submitId == "") {
                    $scope.errorMessage = "No submit id has been entered"
                    return
                }

            }

            var newMenuItem = {
                "name": "",
                "submit": submitId,
                "type": ""
            }

            if (selectedMenuItem.level == 1 && menuItemRelation == 'sibling')
                newMenuItem['class'] = ""
            else
                newMenuItem['parent'] = selectedMenuItem['submit']


            if (menuItemRelation == menuItemRelationList[0].type) {
                newMenuItem['level'] = 1;
                newMenuItem['menuType'] = menuItemRelationList[0]
            }
            else if (menuItemRelation == menuItemRelationList[1].type) {
                newMenuItem['level'] = 2;
                newMenuItem['menuType'] = menuItemRelationList[1]
            }
            else if (menuItemRelation == menuItemRelationList[2].type) {
                newMenuItem['level'] = selectedMenuItem['level'] + 1;
                newMenuItem['menuType'] = menuItemRelationList[2]
            }
            else if (menuItemRelation == menuItemRelationList[3].type) {
                newMenuItem['level'] = selectedMenuItem['level'] + 1;
                newMenuItem['menuType'] = menuItemRelationList[3]
            }

            var selectedMenuItemIndex = getMenuItemIndex(selectedMenuItem);
            addElemetToMenuDict(newMenuItem, selectedMenuItemIndex);
            $('#newMenuItemModalWindow').modal('hide');
        }
    }

    var getMenuItemIndex = function (menuItem) {
        for (var i = 0; i < $scope.flatMenuDict.length; i++) {
            if ($scope.flatMenuDict[i].submit == menuItem.submit) {
                return i;
            }
        }
    }

    var addElemetToMenuDict = function (newMenuItem, index) {
        $scope.flatMenuDict.splice(index + 1, 0, newMenuItem);
    }

    var getMenuFileSuccessCallback = function (data, status) {

        $scope.menuDict = data;
        var menuItemRelationList = $scope.modalWindowsInformation.menuItemRealtionDropDown.values;

        for (var i = 0; i < data.left.length; i++) {
            var menuItem = data.left[i];
            menuItem['level'] = 1;
            menuItem['menuType'] = menuItemRelationList[0]
            $scope.flatMenuDict.push(menuItem);

            for (var j = 0; j < menuItem['children'].length; j++) {
                var childItem = menuItem['children'][j];
                childItem['level'] = 2;
                childItem['parent'] = menuItem['submit']
                childItem['menuType'] = menuItemRelationList[1]
                $scope.flatMenuDict.push(childItem);

                for (var k = 0; k < childItem['submenu'].length; k++) {
                    var submenuItem = childItem['submenu'][k];
                    submenuItem['level'] = 3;
                    submenuItem['parent'] = childItem['submit']
                    submenuItem['menuType'] = menuItemRelationList[2]
                    $scope.flatMenuDict.push(submenuItem);

                    for (var l = 0; l < submenuItem['list'].length; l++) {
                        var listItem = submenuItem['list'][l];
                        listItem['level'] = 4;
                        listItem['parent'] = submenuItem['submit']
                        listItem['menuType'] = menuItemRelationList[3]
                        $scope.flatMenuDict.push(listItem);
                    }
                    submenuItem['list'] = []
                }
                childItem['submenu'] = []
            }

            for (var j = 0; j < menuItem['submenu'].length; j++) {
                var submenuItem = menuItem['submenu'][j];
                submenuItem['level'] = 2;
                submenuItem['parent'] = menuItem['submit']
                submenuItem['menuType'] = menuItemRelationList[2]
                $scope.flatMenuDict.push(submenuItem);

                for (var l = 0; l < submenuItem['list'].length; l++) {
                    var listItem = submenuItem['list'][l];
                    listItem['level'] = 3;
                    listItem['parent'] = submenuItem['submit']
                    listItem['menuType'] = menuItemRelationList[3]
                    $scope.flatMenuDict.push(listItem);
                }
                submenuItem['list'] = []
            }
            menuItem['children'] = []
        }
    };

    var errorCallback = function (data, status, headers, config) {
        alert(data.ExceptionMessage);
    };

    informationFactory.getFile("menu").success(getMenuFileSuccessCallback).error(errorCallback);

});
