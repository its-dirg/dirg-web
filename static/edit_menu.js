var app = angular.module("editMenuApp", [])

app.factory('informationFactory', function ($http) {
    return {
        getFile: function (name) {
            return $http.get("/file?name=" + name);
        },

        postLeftMenu: function (menu, side) {
            return $http.post("/post_left_menu", {"menu": menu, "side": side});
        }
    }
});

app.controller("HelloController", function ($scope, informationFactory) {

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

    $scope.menuSideDropdown = {
        "value": "left",
        "values": [
            {
                "type": "left",
                "name": "Left menu"
            },
            {
                "type": "right",
                "name": "Right menu"
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

    $scope.rootModalWindowsInformation = {
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
                }
            ]
        },
        "submitId": ""
    }

    $scope.dropdownModalWindowsInformation = {
        "menuItemRealtionDropDown": {
            "value": "child",
            "values": [
                {
                    "type": "child",
                    "name": "Drop-down item"
                },
                {
                    "type": "header",
                    "name": "Page header"
                }
            ]
        },
        "submitId": ""
    }

    $scope.headerModalWindowsInformation = {
        "menuItemRealtionDropDown": {
            "value": "submenu",
            "values": [
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
                currentMenuItem['submenu'] = []
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
        for (var j = 0; j < originalMenuDict.length; j++) {
            if (originalMenuDict[j].children.length > 0) {
                originalMenuDict[j]['class'] = "dropdown"
            }
        }
    }

    function s4() {
        return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
    }

    var guid = function () {
        return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
            s4() + '-' + s4() + s4() + s4();
    };

    var removeUnusedAttributes = function () {
        for (var i = 0; i < originalMenuDict.length; i++) {
            delete originalMenuDict[i]["level"];
            delete originalMenuDict[i]["menuType"]
            delete originalMenuDict[i]["guid"]
            var levelTwoMenuItems = originalMenuDict[i].children;

            for (var j = 0; j < levelTwoMenuItems.length; j++) {
                delete levelTwoMenuItems[j]["level"];
                delete levelTwoMenuItems[j]["parent"];
                delete levelTwoMenuItems[j]["menuType"]
                delete levelTwoMenuItems[j]["guid"]
                var levelThreeMenuItems = originalMenuDict[i].children[j].submenu;

                if (levelThreeMenuItems == null)
                    continue

                for (var k = 0; k < levelThreeMenuItems.length; k++) {
                    delete levelThreeMenuItems[k]["level"];
                    delete levelThreeMenuItems[k]["parent"];
                    delete levelThreeMenuItems[k]["menuType"]
                    delete levelThreeMenuItems[k]["guid"]
                    var levelFourMenuItems = originalMenuDict[i].children[j].submenu[k].list;

                    if (levelFourMenuItems == null)
                        continue

                    for (var l = 0; l < levelFourMenuItems.length; l++) {
                        delete levelFourMenuItems[l]["level"];
                        delete levelFourMenuItems[l]["parent"];
                        delete levelFourMenuItems[l]["menuType"]
                    }
                }
            }

            levelTwoMenuItems = originalMenuDict[i].submenu;
            for (var m = 0; m < levelTwoMenuItems.length; m++) {
                delete levelTwoMenuItems[m]["level"];
                delete levelTwoMenuItems[m]["parent"];
                delete levelTwoMenuItems[m]["menuType"]
                var levelThreeMenuItems = originalMenuDict[i].submenu[m].list;

                for (var n = 0; n < levelThreeMenuItems.length; n++) {
                    delete levelThreeMenuItems[n]["level"];
                    delete levelThreeMenuItems[n]["parent"];
                    delete levelThreeMenuItems[n]["menuType"]
                }
            }
        }
    }

    function clearAndUpdateMenuDict() {
        $scope.flatMenuDict = [];
        originalMenuDict = []
        informationFactory.getFile("menu").success(getMenuFileSuccessCallback).error(errorCallback);
    }

    var getPostMenuSuccessCallback = function (data, status) {
        alert("Menu saved successfully!");
        clearAndUpdateMenuDict();
    }


    $scope.saveMenu = function () {

        //Switch the menu back so that level 1 contains sub menu and so on
        convertToOriginalMenuStructure();

        //Add the dropdown attribute to the level 1 menu items it the are any children
        addDropDownAttribute();

        removeUnusedAttributes();

        informationFactory.postLeftMenu(originalMenuDict, $scope.menuSideDropdown.value).success(getPostMenuSuccessCallback).error(errorCallback);
    }

    function getMenuRelationsOptions(menuType) {
        return $scope.modalWindowsInformation.menuItemRealtionDropDown.values;
    }

    var addSecondLevelMenuToParent = function (menuItem) {
        var menuItemTypes = getMenuRelationsOptions(menuItem.menuType);

        for (var i = 0; i < originalMenuDict.length; i++) {
            if (originalMenuDict[i].guid == menuItem.parent) {
                var parentMenuItem = jQuery.extend(true, {}, originalMenuDict[i]);

                if (menuItem.menuType.type == menuItemTypes[1].type) {
                    menuItem['submenu'] = []
                    parentMenuItem['children'].push(menuItem)
                }
                else if (menuItem.menuType.type == menuItemTypes[2].type) {
                    menuItem['list'] = []
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
                var secondLevelChild = jQuery.extend(true, {}, originalMenuDict[i].children[j]);
                if (secondLevelChild.guid == menuItem.parent) {
                    menuItem['list'] = []
                    secondLevelChild['submenu'].push(menuItem)
                    originalMenuDict[i].children[j] = secondLevelChild;
                    break;
                }
            }

            for (var k = 0; k < originalMenuDict[i].submenu.length; k++) {
                var secondLevelSubmenu = jQuery.extend(true, {}, originalMenuDict[i].submenu[k]);
                if (secondLevelSubmenu.guid == menuItem.parent) {
                    secondLevelSubmenu['list'].push(menuItem)
                    originalMenuDict[i].submenu[k] = secondLevelSubmenu;
                    break;
                }
            }
        }
    }

    var addForthLevelMenuToParent = function (menuItem) {
        for (var i = 0; i < originalMenuDict.length; i++) {
            for (var j = 0; j < originalMenuDict[i].children.length; j++) {
                if (originalMenuDict[i].children[j].submenu == null)
                    continue

                for (var k = 0; k < originalMenuDict[i].children[j].submenu.length; k++) {
                    var thirdLevelMenuDict = jQuery.extend(true, {}, originalMenuDict[i].children[j].submenu[k]);

                    if (thirdLevelMenuDict.guid == menuItem.parent) {
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
                if (menuItem.guid == $scope.flatMenuDict[index].parent) {
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
        $('#newMenuItemModalWindow').modal('show');
        $scope.selectedMenuItem = menuItem;
    }

    $scope.errorMessage = ""

    function getSelectedMenuRelation() {
        if ($scope.selectedMenuItem.menuType == getAllMenuReations()[0])
            return $scope.rootModalWindowsInformation.menuItemRealtionDropDown.value;
        else if ($scope.selectedMenuItem.menuType == getAllMenuReations()[1])
            return $scope.dropdownModalWindowsInformation.menuItemRealtionDropDown.value;
        else if ($scope.selectedMenuItem.menuType == getAllMenuReations()[2])
            return $scope.headerModalWindowsInformation.menuItemRealtionDropDown.value;
    }

    function getSelectedSubmitId() {
        return $scope.modalWindowsInformation.submitId;
    }

    function getAllMenuReations() {
        return $scope.modalWindowsInformation.menuItemRealtionDropDown.values
    }

    $scope.submitNewMenuItemModalWindow = function () {
        $scope.errorMessage = ""
        var selectedMenuItem = $scope.selectedMenuItem;
        var selectedMenuItemRelation = getSelectedMenuRelation();
        var menuItemRelationList = getAllMenuReations();
        var submitId = getSelectedSubmitId();

        if (submitId != null) {
            for (var i = 0; i < $scope.flatMenuDict.length; i++) {

                if (submitId == "" && selectedMenuItemRelation == getAllMenuReations()[0].type){
                    break
                }

                if (submitId == $scope.flatMenuDict[i].submit) {
                    $scope.errorMessage = "The submit id you entered is not unique"
                    return
                }

                else if (submitId == "" && selectedMenuItemRelation != getAllMenuReations()[0].type) {
                    $scope.errorMessage = "No submit id has been entered"
                    return
                }

            }

            var newMenuItem = {
                "name": "",
                "submit": submitId,
                "type": $scope.menuItemVisibility.values[0].type
            }

            if (selectedMenuItem.level == 1 && selectedMenuItemRelation == 'sibling')
                newMenuItem['class'] = ""
            else if (selectedMenuItemRelation == selectedMenuItem.menuType.type)
                newMenuItem['parent'] = selectedMenuItem['parent']
            else
                newMenuItem['parent'] = selectedMenuItem['guid']


            if (selectedMenuItemRelation == menuItemRelationList[0].type) {
                newMenuItem['level'] = 1;
                newMenuItem['menuType'] = menuItemRelationList[0]
                newMenuItem['guid'] = guid()
            }
            else if (selectedMenuItemRelation == menuItemRelationList[1].type) {
                newMenuItem['level'] = 2;
                newMenuItem['menuType'] = menuItemRelationList[1]
                newMenuItem['guid'] = guid()
            }
            else if (selectedMenuItemRelation == menuItemRelationList[2].type) {
                newMenuItem['level'] = selectedMenuItem['level'] + 1;
                newMenuItem['menuType'] = menuItemRelationList[2]
                newMenuItem['type'] = $scope.headerVisibility.values[0].type
                newMenuItem['guid'] = guid()
            }
            else if (selectedMenuItemRelation == menuItemRelationList[3].type) {
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
            if ($scope.flatMenuDict[i].guid == menuItem.guid) {
                return i;
            }
        }
    }

    function getNextItemIndexAtSameLevel(index){
        var currentLevel = $scope.flatMenuDict[index].level
        var menuLenght = 0;

        for (var item in $scope.flatMenuDict){
            menuLenght++
        }

        for(var i = index+1; i < menuLenght; i++){
            if ($scope.flatMenuDict[i].level <= currentLevel){
                break
            }
        }
        return i;
    }

    var addElemetToMenuDict = function (newMenuItem, index) {
        var nextIndexAtLevel = getNextItemIndexAtSameLevel(index);

        $scope.flatMenuDict.splice(nextIndexAtLevel, 0, newMenuItem);
    }

    function addChildrenToRootMenu(menuItem, menuItemRelationList) {
        for (var j = 0; j < menuItem['children'].length; j++) {
            var childItem = menuItem['children'][j];
            childItem['level'] = 2;
            childItem['parent'] = menuItem['guid']
            childItem['menuType'] = menuItemRelationList[1]
            childItem['guid'] = guid();
            $scope.flatMenuDict.push(childItem);

            for (var k = 0; k < childItem['submenu'].length; k++) {
                var submenuItem = childItem['submenu'][k];
                submenuItem['level'] = 3;
                submenuItem['parent'] = childItem['guid']
                submenuItem['menuType'] = menuItemRelationList[2]
                submenuItem['guid'] = guid();
                $scope.flatMenuDict.push(submenuItem);

                for (var l = 0; l < submenuItem['list'].length; l++) {
                    var listItem = submenuItem['list'][l];
                    listItem['level'] = 4;
                    listItem['parent'] = submenuItem['guid']
                    listItem['menuType'] = menuItemRelationList[3]
                    $scope.flatMenuDict.push(listItem);
                }
                submenuItem['list'] = []
            }
            childItem['submenu'] = []
        }
    }

    function addSubmenusToRootMenu(menuItem, menuItemRelationList) {
        for (var j = 0; j < menuItem['submenu'].length; j++) {
            var submenuItem = menuItem['submenu'][j];
            submenuItem['level'] = 2;
            submenuItem['parent'] = menuItem['guid']
            submenuItem['menuType'] = menuItemRelationList[2]
            $scope.flatMenuDict.push(submenuItem);

            for (var l = 0; l < submenuItem['list'].length; l++) {
                var listItem = submenuItem['list'][l];
                listItem['level'] = 3;
                listItem['parent'] = submenuItem['guid']
                listItem['menuType'] = menuItemRelationList[3]
                $scope.flatMenuDict.push(listItem);
            }
            submenuItem['list'] = []
        }
    }

    function buildFlattMenuDict(menuItem, menuItemRelationList) {
        menuItem['level'] = 1;
        menuItem['menuType'] = menuItemRelationList[0]
        menuItem['guid'] = guid()
        $scope.flatMenuDict.push(menuItem);

        addChildrenToRootMenu(menuItem, menuItemRelationList);
        addSubmenusToRootMenu(menuItem, menuItemRelationList);
    }

    $scope.setupFlatMenuDict = function () {
        clearAndUpdateMenuDict();
    }

    var getMenuFileSuccessCallback = function (data, status) {
        var menuItemRelationList = getAllMenuReations();

        if ($scope.menuSideDropdown.value == "left") {
            for (var i = 0; i < data.left.length; i++) {
                var menuItem = data.left[i];
                buildFlattMenuDict(menuItem, menuItemRelationList);
            }
        } else if ($scope.menuSideDropdown.value == "right") {
            for (var i = 0; i < data.right.length; i++) {
                var menuItem = data.right[i];
                buildFlattMenuDict(menuItem, menuItemRelationList);
            }
        }
    };

    var errorCallback = function (data, status, headers, config) {
        alert(data.ExceptionMessage);
    };

    informationFactory.getFile("menu").success(getMenuFileSuccessCallback).error(errorCallback);

});
