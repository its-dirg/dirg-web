/**
 * Created by haho0032 on 2013-12-02.
 */

    var app = angular.module('main', ['toaster']);

    app.factory('informationFactory', function ($http) {
        return {
            getInformation: function (page, submeny_header, submeny_page) {
                return $http.get("/information", {params: { "page": page, "submeny_header": submeny_header, "submeny_page": submeny_page}});
            },
            getFile: function (name, callback, toaster, scope) {
                url = "/file?name=" + name
                return $.get(url, callback).fail(function() {toaster.pop('error', "Notification", "Invalid request!"); scope.$apply();});
            },
            saveInformation: function (page, submeny_header, submeny_page, html) {
                return $http.post("/save", { "page": page, "submeny_header": submeny_header, "submeny_page": submeny_page, "html": html});
            },
            changeUserAdmin: function (email, admin) {
                return $http.post("/changeUserAdmin", { "email": email, "admin": admin});
            },
            changeUserValid: function (email, valid) {
                return $http.post("/changeUserValid", { "email": email, "valid": valid});
            },
            changepasswd: function (password, password1, password2) {
                return $http.post("/changepasswd", { "password": password, "password1": password1, "password2": password2});
            },
            deleteUser: function (email) {
                return $http.post("/deleteuser", { "email": email});
            },
            signin: function (user, password) {
                return $http.get("/signin", {params: { "user": user, "password": password}});
            },
            invite: function(forename, surname, email, type){
                return $http.get("/invite", {params: {
                    "forename": forename,
                    "surname": surname,
                    "email": email,
                    "type": type
                }});
            },
            adminUsers: function() {
                return $http.get("/adminUsers");
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
        $scope.submeny_header = "";
        $scope.submeny_page = "";
        //Allows the user to change password
        $scope.allowChangePassword = false;
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
        //Users that can be administrated.
        $scope.users = "";
        //A list with all authentication methods.
        $scope.authMethods = [];
        //The chosen authentication method.
        $scope.authMethod = "";
        //Set to true if you want to allow menu configuration.
        $scope.allowConfig = false;

        //Set to true if you want to allow user to invite other users.
        $scope.allowInvite = false;
        //Allows the user to edit users.
        $scope.allowUserChange = false;
        //Allows the user to view the admin menu.
        $scope.allowAdmin = false;

        //True if the user is changing the menu configurations.
        //This functionality is not fully implemented and do not work!
        $scope.configMenu = false;
        //The headline when the menu is being configured.
        //This functionality is not fully implemented and do not work!
        $scope.configure = "";
        //Temp. menu used during menu configuration.
        //This functionality is not fully implemented and do not work!
        $scope.tmpmenu = "";


        $scope.inviteType = "idp_new";
        $scope.invite_prop = {   "type": "select",
                    "name": "Invite user to sign in with SAML.",
                    "value": "idp_new",
                    "values": [{"type": "idp_new", "name": "Invite new user to sign in with SAML."},
                        {"type": "idp", "name": "Invite existing user to sign in with SAML."},
                        {"type": "pass_new", "name": "Invite new user to sign in with password."},
                        {"type": "pass", "name": "Invite existing user to sign in with password."}]
                };


        var getInformationSuccessCallback = function (data, status, headers, config) {
            $scope.information = data;
            setupSubmenu($scope.menu.right);
            setupSubmenu($scope.menu.left);
            $scope.edit = false;
        };

        var saveInformationSuccessCallback = function (data, status, headers, config) {
            $scope.information = data;
            setupSubmenu($scope.menu.right);
            setupSubmenu($scope.menu.left);
            $scope.edit = false;
            toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        var setupSubmenu = function(menu) {
            breadcrum = "";
            $scope.submenu = [];
            for (var i=0;i<menu.length;i++) {
                if (menu[i].submit == $scope.page) {
                    breadcrum = menu[i].name;
                    handleSubmenu(menu[i].submenu, breadcrum);
                    break;
                }
                if (menu[i].children.length > 0) {
                    for (var j=0;j<menu[i].children.length;j++) {
                        if (menu[i].children[j].submit == $scope.page) {
                            breadcrum = menu[i].name + " -> " + menu[i].children[j].name;
                            handleSubmenu(menu[i].children[j].submenu, breadcrum);
                            break;
                        }
                    }
                }
            }

        }

        var handleSubmenu = function(submenu, breadcrum) {
            if ($scope.submeny_header == "" || $scope.submeny_page == "" || typeof $scope.submeny_header === "undefined" || typeof $scope.submeny_page === "undefined") {
                $scope.submeny_header = submenu[0].submit;
                $scope.submeny_page = submenu[0].list[0].submit;
            }
            if (submenu.length > 0) {
                for (var i=0;i<submenu.length;i++){
                    if (submenu[i].type == "collapse_open") {
                        submenu[i].class = "in";
                    }
                    else if (submenu[i].type == "collapse_close") {
                        submenu[i].class = "";
                    } else {
                        submenu[i].class = "in";
                    }

                    if (submenu[i].submit == $scope.submeny_header) {
                        breadcrum += " -> " + submenu[i].name;
                        if (submenu[i].list.length > 0) {
                            for(var j=0;j<submenu[i].list.length;j++){
                                if (submenu[i].list[j].submit==$scope.submeny_page) {
                                    breadcrum += " -> " + submenu[i].list[j].name;
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            $scope.submenu = submenu;
            $scope.headline = breadcrum;
        }


        var fetchMenuSuccessCallback = function (data, status, headers, config) {
            try {
                $scope.getInformationFromServer(data.left[0].submit);
            } catch(e) {
                try {
                    $scope.getInformationFromServer(data.right[0].submit);
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

        var adminUsersSuccessCallback = function (data, status, headers, config) {
            $scope.users = data;
            $('#modalAdministrateUsers').modal('show');
        };

        var adminUsersSuccessCallbackNoneModal = function (data, status, headers, config) {
            $scope.users = data;
        };

        var changeUserAdminSuccessCallback = function (data, status, headers, config) {
            toaster.pop('success', "Notification", data);
        };

        var changeUserValidSuccessCallback = function (data, status, headers, config) {
            toaster.pop('success', "Notification", data);
        };

        var changepasswdSuccessCallback = function (data, status, headers, config) {
            $('#modalChangePassword').modal('hide');
            toaster.pop('success', "Notification", data);
        };


        var deleteUserSuccessCallback = function (data, status, headers, config) {
            toaster.pop('success', "Notification", data);
            informationFactory.adminUsers().success(adminUsersSuccessCallbackNoneModal).error(errorCallback);

        };


        var inviteSuccessCallback = function (data, status, headers, config) {
         toaster.pop('success', "Notification", data);
            $('#modalInvite').modal('hide');
        };

        var signoutSuccessCallback = function (data, status, headers, config) {
            $scope.handleAuthResponse(data);
            $scope.fetchMenu();
            //toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        var errorCallback = function (data, status, headers, config) {
            toaster.pop('error', "Notification", data["ExceptionMessage"]);
        };

        $scope.errorCallback_ = function (data, status, headers, config) {
            errorCallback(data, status, headers, config);
        };

        $scope.getInformationFromServer = function (page, submeny_header, submeny_page) {
            if (page != "") {
                if (typeof submeny_header !== 'undefined') {
                    $scope.submeny_header = submeny_header;
                    if (typeof submeny_page !== 'undefined') {
                        $scope.submeny_page = submeny_page;
                    }
                } else {
                    $scope.submeny_header = "";
                    $scope.submeny_page = "";
                }
                $scope.allowedEdit = $scope.oldAllowedEdit;
                $scope.page = page;
                informationFactory.getInformation(page,submeny_header, submeny_page).success(getInformationSuccessCallback).error(errorCallback);
            }
        };

        $scope.fetchMenu = function () {
            informationFactory.fetchMenu().success(fetchMenuSuccessCallback).error(errorCallback);
        };

        $scope.setAuthMethod = function () {
            $scope.authMethod = this.prop.value;
        };

        $scope.setInviteType = function () {
            $scope.inviteType = this.invite_prop.value;
        };



        $scope.savePage = function () {
            if ($scope.allowedEdit) {
                informationFactory.saveInformation($scope.page, $scope.submeny_header, $scope.submeny_page, tinymce.activeEditor.getContent()).success(saveInformationSuccessCallback).error(errorCallback);
            }
        };

        $scope.handleAuthResponse = function (authResponse) {
            if (authResponse.authMethods) {
                $scope.prop = {   "type": "select",
                    "name": authResponse.authMethods[0].name,
                    "value": authResponse.authMethods[0].type,
                    "values": authResponse.authMethods
                };
                $scope.authMethods = authResponse.authMethods;
                $scope.authMethod = $scope.authMethods[0].type;
            }
            $scope.allowInvite = authResponse.allowInvite == "true";
            $scope.allowConfig = authResponse.allowConfig == "true";
            $scope.allowedEdit = authResponse.allowedEdit == "true";
            $scope.allowedSignout = authResponse.allowSignout == "true";
            $scope.authenticated = authResponse.authenticated == "true";
            $scope.allowUserChange = authResponse.allowUserChange == "true";
            $scope.allowChangePassword = authResponse.allowChangePassword == "true";

            $scope.allowAdmin = $scope.allowInvite || $scope.allowConfig;

            $scope.oldAllowedEdit = $scope.allowedEdit;
        };

        $scope.submitSignIn = function () {
            var user = this.user;
            var password = this.password;
            this.user = "";
            this.password = "";
            informationFactory.signin(user, password).success(signinSuccessCallback).error(errorCallback);
        };


        $scope.submitChangePassword = function () {
            var password = this.password;
            var password1 = this.password1;
            var password2 = this.password2;
            this.password = "";
            this.password1 = "";
            this.password2 = "";
            informationFactory.changepasswd(password, password1, password2).success(changepasswdSuccessCallback).error(errorCallback);
        };

        $scope.submitInvite = function () {
            var forename = this.forename;
            var surname = this.surname;
            var email = this.email;
            this.forename = "";
            this.surname = "";
            this.email = "";
            informationFactory.invite(forename, surname, email, this.invite_prop.value).success(inviteSuccessCallback).error(errorCallback);
        };

        $scope.closeSigning = function () {
            this.user = "";
            this.password = "";
            $('#modalSignin').modal('hide');
        };

        $scope.signin = function () {
            $('#modalSignin').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        $scope.changePassword = function () {
            $('#modalChangePassword').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        $scope.closeChangePassword = function () {
            this.password = "";
            this.password1 = "";
            this.password2 = "";
            $('#modalSignin').modal('hide');
        };

        $scope.invite = function () {
            $('#modalInvite').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        $scope.adminUsers = function () {
            informationFactory.adminUsers().success(adminUsersSuccessCallback).error(errorCallback);
        };


        $scope.deleteUser = function (email) {
            /*if (confirm("Are you sure you want to delete the user with email " + email + "?")) {
                informationFactory.deleteUser(email).success(deleteUserSuccessCallback).error(errorCallback);
            }*/
            bootbox.confirm("Are you sure you want to delete the user with email " + email + "?",
                function (result) {
                    if (result) {
                        informationFactory.deleteUser(email).success(deleteUserSuccessCallback).error(errorCallback);
                        $scope.$apply();
                    }

                }
            );
        };

        $scope.changeUserAdmin = function (email) {
            var admin = -1;
            if (this.admin == true) {
                admin = 1;
            } else {
                admin = 0;
            }
            informationFactory.changeUserAdmin(email, admin).success(changeUserAdminSuccessCallback).error(errorCallback);
        };

        $scope.changeUserValid = function (email, valid) {
            valid = -1;
            if (this.valid == true) {
                valid = 1;
            } else {
                valid = 0;
            }
            informationFactory.changeUserValid(email, valid).success(changeUserValidSuccessCallback).error(errorCallback);
        };

        $scope.changePassword = function () {
            $('#modalChangePassword').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        $scope.signout = function () {
            informationFactory.signout().success(signoutSuccessCallback).error(errorCallback);
        };

        var getMenuFileSuccessCallback = function (data, status) {
            $scope.editFile($scope.menu.editmenu, "menu", "You can edit the menu on this page.", data);
            $scope.$apply();
        };

        var getCSSFileSuccessCallback = function (data, status) {
            $scope.editFile($scope.menu.css, "css", "Here you can edit your custom css.", data);
            $scope.$apply();
        };

        $scope.editCSS = function () {
            informationFactory.getFile("css", getCSSFileSuccessCallback, toaster, $scope);
        };

        $scope.editMenu = function () {
            informationFactory.getFile("menu", getMenuFileSuccessCallback, toaster, $scope);
        };

        $scope.editFile = function (header, name, text, filetext) {
            $scope.edit = false;
            $scope.oldHeadline = $scope.headline;
            $scope.headline = header;
            $scope.configMenu = true;
            $scope.oldAllowedEdit = $scope.allowedEdit;
            $scope.allowedEdit = false;
            $scope.information = text +
                '<form action="savefile" class="form" role="form" method="post">' +
                    '<input type="hidden" id="name" name="name" ng-model="name" value="' + name + '" >' +
                    '<button type="submit" class="btn btn-primary">Save</button>' +
                    '<div class="form-group">' +
                        '<textarea id="filetext" name="filetext" rows="10" cols="100" >' + filetext + '</textarea>' +
                    '</div>' +
                    '<button type="submit" class="btn btn-primary">Save</button>' +
                '</form>'
        };

        $scope.editPage = function () {
            $scope.edit = $scope.allowedEdit;

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

