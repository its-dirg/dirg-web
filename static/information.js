/**
 * Created by haho0032 on 2013-12-02.
 */
    var app = angular.module('main', ['toaster']);

    app.factory('informationFactory', function ($http) {
        return {
            getInformation: function (page) {
                return $http.get("/information", {params: { "page": page}});
            },
            saveInformation: function (page, html) {
                return $http.post("/save", { "page": page, "html": html});
            },
            signin: function (user, password) {
                return $http.get("/signin", {params: { "user": user, "password": password}});
            },
            signout: function () {
                return $http.post("/signout", {});
            },
            fetchMenu: function () {
                return $http.post('/menu', {});
            }
        };
    });

    //Controller which will be executed when the web page is loaded
    app.controller('InformationCtrl', function ($scope, informationFactory, toaster) {

        //The current information(HTML) for the page.
        $scope.information = "";
        //True if the user is editing a page, otherwise false.
        $scope.edit = false;
        //The current page the user is viewing.
        $scope.page = "";
        //Allows the user to sign out.
        $scope.allowSignout = true;
        //Allows the user to edit pages.
        $scope.allowedEdit = false;
        //The headline for the page.
        $scope.headline = "";
        //True if the user is authenticated, otherwise false.
        $scope.authenticated = false;
        //The current menu for the user.
        $scope.menu = "";
        //A list with all authentication methods.
        $scope.authMethods = [];
        //The chosen authentication method.
        $scope.authMethod = ""
        //Set to true if you want to allow menu configuration.
        //This functionality is not fully implemented and do not work!
        $scope.allowConfig = false;
        //True if the user is changing the menu configurations.
        //This functionality is not fully implemented and do not work!
        $scope.configMenu = false;
        //The headline when the menu is being configured.
        //This functionality is not fully implemented and do not work!
        $scope.configure = "";
        //Temp. menu used during menu configuration.
        //This functionality is not fully implemented and do not work!
        $scope.tmpmenu = "";


        var getInformationSuccessCallback = function (data, status, headers, config) {
            $scope.information = data;
            $scope.edit = false;
        };

        var saveInformationSuccessCallback = function (data, status, headers, config) {
            $scope.information = data;
            $scope.edit = false;
            toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        var fetchMenuSuccessCallback = function (data, status, headers, config) {
            try {
                $scope.configure = data.configure;
                $scope.getInformationFromServer(data.left[0].submit, data.left[0].name);
            } catch(e) {
                try {
                    $scope.getInformationFromServer(data.right[0].submit, data.left[0].name);
                } catch(e) {

                }
            }
            $scope.menu=data;
        };

        var signinSuccessCallback = function (data, status, headers, config) {
            $('#modalSignin').modal('hide');
            $scope.handleAuthResponse(data);
            $scope.fetchMenu();
            //toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        var signoutSuccessCallback = function (data, status, headers, config) {
            $scope.handleAuthResponse(data);
            $scope.fetchMenu();
            //toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        var errorCallback = function (data, status, headers, config) {
            toaster.pop('error', "Notification", data["ExceptionMessage"]);
        };

        $scope.errorCallback_ = function(data, status, headers, config) {
            errorCallback(data, status, headers, config);
        }

        $scope.getInformationFromServer = function (page, name) {
            if (page != "") {
                $scope.headline=name;
                $scope.page = page;
                informationFactory.getInformation(page).success(getInformationSuccessCallback).error(errorCallback);
            }
        };

        $scope.fetchMenu = function () {
            informationFactory.fetchMenu().success(fetchMenuSuccessCallback).error(errorCallback);
        };


        $scope.setAuthMethod = function() {
            $scope.authMethod = this.prop.value;
        }

        $scope.savePage = function () {
            if ($scope.allowedEdit) {
                informationFactory.saveInformation($scope.page, tinymce.activeEditor.getContent()).success(saveInformationSuccessCallback).error(errorCallback);
            }
        };

        $scope.handleAuthResponse = function(authResponse) {
            if (authResponse.authMethods) {
                $scope.prop = {   "type": "select",
                    "name": authResponse.authMethods[0].name,
                    "value": authResponse.authMethods[0].type,
                    "values": authResponse.authMethods
                };
                $scope.authMethods = authResponse.authMethods;
                $scope.authMethod = $scope.authMethods[0].type;
            }
            $scope.allowConfig = authResponse.allowConfig == "true";
            $scope.allowedEdit = authResponse.allowedEdit == "true";
            $scope.allowedSignout = authResponse.allowSignout == "true";
            $scope.authenticated = authResponse.authenticated == "true";
        }

        $scope.submitSignIn = function () {
            informationFactory.signin(this.user, this.password).success(signinSuccessCallback).error(errorCallback);
        };

        $scope.closeSigning = function () {
            $('#modalSignin').modal('hide');
        };

        $scope.signin = function () {
            $('#modalSignin').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        $scope.signout = function () {
            informationFactory.signout().success(signoutSuccessCallback).error(errorCallback);
        };

        $scope.editMenu = function () {
            $scope.oldHeadline = $scope.headline;
            $scope.headline = $scope.configure;
            $scope.configMenu = true;
            $scope.oldAllowedEdit = $scope.allowedEdit
            $scope.allowedEdit = false;
            $scope.information = ""
        };

        $scope.saveMenu = function () {
            $scope.configMenu = false;
            $scope.allowedEdit = $scope.oldAllowedEdit;
            $scope.getInformationFromServer($scope.page, $scope.oldHeadline);
        };

        $scope.editPage = function () {
            if ($scope.allowedEdit) {
                $scope.edit = true;
            } else {
                $scope.edit = false;
            }

        };

    });


    app.directive('changeMenuValue', function() {
      return function(scope, element) {
        element.bind('change', function() {
          //element.attr('id')
          //element.val();
        });
      };
    });

    app.directive('editmenu', function($http) {
            return {
                restrict: 'A',
                templateUrl: '/static/templateConfigMenu.html',
                link: function(scope, element, attrs) {
                    scope.$watch('configMenu', function (val) {
                        if (val == true){
                            scope.tmpmenu = scope.menu;
                        } else {
                            scope.tmpmenu = "";
                        }
                    });
                }
            }
    });


    app.directive('menu', function($http) {
            return {
                restrict: 'A',
                templateUrl: '/static/templateMenu.html',
                link: function(scope, element, attrs) {
                    scope.fetchMenu();
                }

            }

    });

    app.directive('edit', function($http) {
            return {
                restrict: 'A',
                //template: '<textarea id="information" name="information" class="information" ng-show="edit == true" style="width:100%">{{information}}</textarea>',
                link: function(scope, element, attrs) {
                    $http.get('/auth').success(function(data) {
                        scope.handleAuthResponse(data);
                    }).error(scope.errorCallback_);
                    scope.$watch('edit', function (val) {
                        if (val) {
                            var textareaTag = document.createElement('textarea');
                            textareaTag.id ="information";
                            textareaTag.name ="information";
                            textareaTag.innerHTML = scope.information;
                            element[0].appendChild(textareaTag);
                            tinymce.init({
                                selector: "textarea#information",
                                plugins: [
                                    "advlist autolink link image lists charmap print preview hr anchor pagebreak spellchecker",
                                    "searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking",
                                    "save table contextmenu directionality emoticons template paste textcolor"
                                ]
                            });
                        } else {
                            element[0].innerHTML="";
                        }
                    });
                }

            }
    });

