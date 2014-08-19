/**
 * Created by haho0032 on 2013-12-02.
 */
    $("[data-toggle='tooltip']").tooltip();

    function max_iframe() {
        var max_icon = $("#max_icon");
        max_icon.addClass("hide_icon");
        max_icon.removeClass("show_icon");
        var min_icon = $("#min_icon");
        min_icon.addClass("show_icon");
        min_icon.removeClass("hide_icon");
        $("#frame_div").addClass("overlay");
    }

    function min_iframe() {
        var min_icon = $("#min_icon");
        min_icon.addClass("hide_icon");
        min_icon.removeClass("show_icon");
        var max_icon = $("#max_icon");
        max_icon.addClass("show_icon");
        max_icon.removeClass("hide_icon");
        $("#frame_div").removeClass("overlay");
    }

    //The initiation of app is moved to the mako folder.
    //var app = angular.module('main', ['toaster']).constant("serviceBasePath", "https://localhost:4646")

    //Initialization of the angularjs factory informationFactory.
    app.factory('informationFactory', function ($http, serviceBasePath) {
        return {
            /**
             * Retrivies the HTML content for a CMS page.
             * @param page           The submit value for a page in the menu.
             * @param submenu_header The sumbit value for a submenu. (May be empty)
             * @param submenu_page   The submit value for a list element in submenu. (May be empty)
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());

             */
            getInformation: function (page, submenu_header, submenu_page) {
                return $http.get(serviceBasePath + "/information", {params: { "page": page, "submenu_header": submenu_header, "submenu_page": submenu_page}});
            },
            /**
             * Retrives the text for a menu file or custom css file.
             * @param name      "menu" for menu file or "css" for the custom css file.
             * @param callback  Callback function for a successfull response.
             * @param toaster   Toaster object, to present error message.
             * @param scope     Angularjs scope.
             * @returns Jquery $.get object
             */
            getFile: function (name, callback, toaster, scope) {
                url = serviceBasePath + "/file?name=" + name
                return $.get(url, callback).fail(function() {toaster.pop('error', "Notification", "Invalid request!"); scope.$apply();});
            },
            /**
             * Will save the HTML content for a CMS page.
             * @param page           The submit value for a page in the menu.
             * @param submenu_header The sumbit value for a submenu. (May be empty)
             * @param submenu_page   The submit value for a list element in submenu. (May be empty)
             * @param html           The HTML text as a string.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            saveInformation: function (page, submenu_header, submenu_page, html) {
                return $http.post(serviceBasePath + "/save", { "page": page, "submenu_header": submenu_header, "submenu_page": submenu_page, "html": html});
            },
            /**
             * Will change administrator status for a user.
             * @param email E-mail for the user.
             * @param admin 1=set user to admin, otherwise 0.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            changeUserAdmin: function (email, admin) {
                return $http.post(serviceBasePath + "/changeUserAdmin", { "email": email, "admin": admin});
            },
            /**
             * Will change valid status for a user. An invalid user is a banned user.
             * @param email E-mail for the user.
             * @param valid 1=sets user to valid and 0= sets user to banned.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            changeUserValid: function (email, valid) {
                return $http.post(serviceBasePath + "/changeUserValid", { "email": email, "valid": valid});
            },
            /**
             * Changes password for a loged in user.
             * @param password  Current password.
             * @param password1 New password.
             * @param password2 New passwword.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            changepasswd: function (password, password1, password2) {
                return $http.post(serviceBasePath + "/changepasswd", { "password": password, "password1": password1, "password2": password2});
            },
            /**
             * Deletes a user from the application.
             * @param email E-mail for the user.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            deleteUser: function (email) {
                return $http.post(serviceBasePath + "/deleteuser", { "email": email});
            },
            /**
             * Signs in a user with username/password.
             * @param user      Username for the user.
             * @param password  The password connected to the given username.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            signin: function (user, password) {
                return $http.get(serviceBasePath + "/signin", {params: { "user": user, "password": password}});
            },
            /**
             * Invite a new user to the application. Will send an inventation with e-mail.
             * @param forename First name for the user.
             * @param surname  Last name for the user.
             * @param email    E-mail for the user.
             * @param type     Type of authentication method. Can be "pass", "idp", "pass_new" or "idp_new".
             *                 pass     = invite an existing user to use username/password.
             *                 idp      = invite an existing user to use SAML IdP.
             *                 pass_new = invite a new user to use username/password.
             *                 idp_new  = invite a new user to use SAML IdP.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            invite: function(forename, surname, email, type){
                return $http.get(serviceBasePath + "/invite", {params: {
                    "forename": forename,
                    "surname": surname,
                    "email": email,
                    "type": type
                }});
            },
            /**
             * Retrieves all users that can be administrated.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            adminUsers: function() {
                return $http.get(serviceBasePath + "/adminUsers");
            },
            /**
             * Sign out the user in the application session.
             *
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            signout: function () {
                return $http.post(serviceBasePath + "/signout", {});
            },
            /**
             * Fetch the menu for the application session user.
             * @returns A object returnobject, where the following methods should be called
             *          returnobject.success(sucess_callback_function()).error(error_callback_function());
             */
            fetchMenu: function () {
                return $http.post(serviceBasePath + '/menu', {});
            }
        };
    });

    //Controller which will be executed when the web page is loaded
    app.controller('InformationCtrl', function ($scope, informationFactory, toaster) {

        //The current information(HTML) for the page.
        $scope.information = "";
        //True if the user is editing a page, otherwise false.
        $scope.edit = false;
        //The current page the user is viewing. The submit value for a page in the menu.
        $scope.page = "";
        //True if the submenu can be visible to the user, otherwise false.
        $scope.hideSubmenu = false;
        //The id for the current submenu. The sumbit value for a submenu. (May be empty)
        $scope.submenu_header = "";
        //The id for the current submenu page. The submit value for a list element in submenu. (May be empty)
        $scope.submenu_page = "";
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
        //True if the page is a iframe.
        $scope.iframe = false;
        //The src for the iframe.
        $scope.iframe_src = "";
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
        //The current invite type.
        //pass     = invite an existing user to use username/password.
        //idp      = invite an existing user to use SAML IdP.
        //pass_new = invite a new user to use username/password.
        //idp_new  = invite a new user to use SAML IdP.
        $scope.inviteType = "idp_new";
        //Properties for the inventation dropdown.
        $scope.invite_prop = {   "type": "select",
                    "name": "Invite user to sign in with SAML.",
                    "value": "idp_new",
                    "values": [{"type": "idp_new", "name": "Invite new user to sign in with SAML."},
                        {"type": "idp", "name": "Invite existing user to sign in with SAML."},
                        {"type": "pass_new", "name": "Invite new user to sign in with password."},
                        {"type": "pass", "name": "Invite existing user to sign in with password."}]
                };


        /**
         * Handles the response from the application server when HTML content for a CMS page is retrieved.
         */
        var getInformationSuccessCallback = function (data, status, headers, config) {

            if (data.iframe_src.trim().length > 0) {
                $scope.iframe = true;
                $scope.iframe_src = data.iframe_src;
                $scope.information = ' ';
                $('#formContainer').css('height','70%');
            } else {
                $scope.iframe = false;
                $scope.iframe_src = '';
                $scope.information = data.html;
                $('#formContainer').height('');
            }

            $scope.submenu_header = data.submenu_header;
            $scope.submenu_page = data.submenu_page;
            $scope.page = data.page;
            $scope.hideSubmenu = false;
            breadcrum = "";
            $scope.submenu = [];
            breadcrum = setupSubmenu($scope.menu.right, breadcrum);
            breadcrum = setupSubmenu($scope.menu.left, breadcrum);
            $scope.headline = breadcrum;
            pageurl = "/page/"+$scope.page;
            if ($scope.submenu_header != "") {
                pageurl =pageurl + "/" + $scope.submenu_header
                if ($scope.submenu_page != "") {
                    pageurl = pageurl + "/" + $scope.submenu_page
                }
            }
            window.history.pushState({path:pageurl},'',pageurl);
            $scope.edit = false;
            //$scope.$apply();
        };

        /**
         * Will find and configure the submenu for the current page.
         * @param menu      Right($scope.menu.right) or left($scope.menu.left) top menu.
         * @param breadcrum The current breadcrum.
         * @returns The new breadcrum.
         */
        var setupSubmenu = function(menu, breadcrum) {
            for (var i=0;i<menu.length;i++) {
                if (menu[i].submit == $scope.page) {
                    breadcrum = menu[i].name;
                    if (menu[i].submenu.length > 0) {
                        breadcrum = handleSubmenu(menu[i].submenu, breadcrum);
                    }
                    break;
                }
                if (menu[i].children.length > 0) {
                    for (var j=0;j<menu[i].children.length;j++) {
                        if (menu[i].children[j].submit == $scope.page) {
                            breadcrum = menu[i].name + " -> " + menu[i].children[j].name;
                            if (menu[i].children[j].submenu.length > 0){
                                breadcrum = handleSubmenu(menu[i].children[j].submenu, breadcrum);
                            }
                            break;
                        }
                    }
                }
            }
            return breadcrum
        }

        /**
         * Will configure a given submenu.
         * @param submenu   The submenu to be configured.
         * @param breadcrum The current breadcrum.
         * @returns The new breadcrum.
         */
        var handleSubmenu = function(submenu, breadcrum) {
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
                    if (submenu[i].submit == $scope.submenu_header) {
                        breadcrum += " -> " + submenu[i].name;
                        if (submenu[i].list.length > 0) {
                            for(var j=0;j<submenu[i].list.length;j++){
                                if (submenu[i].list[j].submit==$scope.submenu_page) {
                                    breadcrum += " -> " + submenu[i].list[j].name;
                                    break;
                                }
                            }
                        }
                    }
                }
            }
            $scope.submenu = submenu;
            return breadcrum
        }

        /**
         * Handles the response from the application server when a menu is returned.
         */
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

        /**
         * Handles the response from the application server when user signed in with username/password.
         */
        var signinSuccessCallback = function (data, status, headers, config) {
            $('#modalSignin').modal('hide');
            $scope.handleAuthResponse(data);
            $scope.fetchMenu();
            //toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        /**
         * Handles the response from the application server when a list of user that can be administrated is returned.
         * Using modal window.
         */
        var adminUsersSuccessCallback = function (data, status, headers, config) {
            $scope.users = data;
            $('#modalAdministrateUsers').modal('show');
        };

        /**
         * Handles the response from the application server when a list of user that can be administrated is returned.
         * Not using modal window.
         */
        var adminUsersSuccessCallbackNoneModal = function (data, status, headers, config) {
            $scope.users = data;
        };

        /**
         *  Handles the response from the application server when a the administrator flag for a user has been changed.
         */
        var changeUserAdminSuccessCallback = function (data, status, headers, config) {
            toaster.pop('success', "Notification", data);
        };

        /**
         *  Handles the response from the application server when a the valid flag for a user has been changed.
         */
        var changeUserValidSuccessCallback = function (data, status, headers, config) {
            toaster.pop('success', "Notification", data);
        };

        /**
         *  Handles the response from the application server when a the user changed password.
         */
        var changepasswdSuccessCallback = function (data, status, headers, config) {
            $('#modalChangePassword').modal('hide');
            toaster.pop('success', "Notification", data);
        };

        /**
         *  Handles the response from the application server when a user has been removed.
         */
        var deleteUserSuccessCallback = function (data, status, headers, config) {
            toaster.pop('success', "Notification", data);
            informationFactory.adminUsers().success(adminUsersSuccessCallbackNoneModal).error(errorCallback);

        };

        /**
         *  Handles the response from the application server when a user been invited to use the application.
         */
        var inviteSuccessCallback = function (data, status, headers, config) {
         toaster.pop('success', "Notification", data);
            $('#modalInvite').modal('hide');
        };


        /**
         *  Handles the response from the application server when a user sign out.
         */
        var signoutSuccessCallback = function (data, status, headers, config) {
            $scope.handleAuthResponse(data);
            $scope.fetchMenu();
            //toaster.pop('success', "Notification", "Successfully saved the page!");
        };

        /**
         *  Handles error responses from the application server.
         */
        var errorCallback = function (data, status, headers, config) {
            toaster.pop('error', "Notification", data["ExceptionMessage"]);
        };

        /**
         *  Handles error responses from the application server.
         */
        $scope.errorCallback_ = function (data, status, headers, config) {
            errorCallback(data, status, headers, config);
        };


        /**
         * Retrieves HTML content for a CMS page.
         * @param page           The submit value for a page in the menu.
         * @param submenu_header The sumbit value for a submenu. (May be empty)
         * @param submenu_page   The submit value for a list element in submenu. (May be empty)
         */
        $scope.getInformationFromServer = function (page, submenu_header, submenu_page) {
            if (page != "") {
                $scope.allowedEdit = $scope.oldAllowedEdit;
                informationFactory.getInformation(page,submenu_header, submenu_page).success(getInformationSuccessCallback).error(errorCallback);
            }
        };

        /**
         * Will fetch the current menu.
         */
        $scope.fetchMenu = function () {
            informationFactory.fetchMenu().success(fetchMenuSuccessCallback).error(errorCallback);
        };

        /**
         * Will set how the user wants to authentice.
         *
         * Will also update the web page.
         *
         * Parameters are sent with angluarjs ng-model="prop.value"
         * @ng-model-param prop.value Prefered authentication method. Can be pass for password and idp for SAML IdP.
         */
        $scope.setAuthMethod = function () {
            $scope.authMethod = this.prop.value;
        };

        /**
         * Will set what kind of invite that should be sent.
         *
         * Will also update the web page.
         *
         * Parameters are sent with angluarjs ng-model="invite_prop.value"
         * @ng-model-param prop.value Prefered authentication method. Can be:
         *        pass     = existing user with username/password.
         *        pass_new = new user with username/password.
         *        idp      = existing user with SAML IdP.
         *        idp_new  = new user with SAML IdP.
         */
        $scope.setInviteType = function () {
            $scope.inviteType = this.invite_prop.value;
        };


        /**
         * Will save the current HTML page that is beeing edited with tinymce.
         * @param shouldContinueEdit    boolean value whether the the page content should be reloaded or just continue
         *                              editing
         */
        $scope.savePage = function (shouldContinueEdit) {
            if ($scope.allowedEdit) {
                var request = informationFactory.saveInformation($scope.page, $scope.submenu_header, $scope.submenu_page, tinymce.activeEditor.getContent()).error(errorCallback);
                request.success(function(data, status, headers, config){
                    $scope.information = data;
                    $scope.edit = shouldContinueEdit;
                    toaster.pop('success', "Notification", "Successfully saved the page!");
                });
            }
        };

        /**
         * This method will handle the autentication response.
         * The response is actually the authorizartions  for the current user.
         * @param authResponse The users authorizations in the application. Not a security layer, only for presentation.
            '{"authenticated": "true",
            "allowSignout": "true",
            "allowUserChange": "true",
            "allowedEdit": "true",
            "allowConfig": "false",
            "allowInvite": "true",
            "allowChangePassword": "true"}'

            Description:
            authenticated:       True if the user is authenticated.
            allowSignout:        True if the user can sign out from the application.
            allowUserChange:     True if the user is allowed to administrate users.
            allowedEdit:         True if the user is allowed to edit pages.
            allowConfig:         True if the user is allowed to configure menu and css files.
            allowInvite:         True if the user is allowed to invite other users.
            allowChangePassword: True if the user is allowed to change the password.
         */
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

        /**
         * Sign in a user with username/password.
         *
         * Parameters are sent with angluarjs ng-model="user" and ng-model="password"
         *
         * @ng-model-param user     The username.
         * @ng-model-param password The password for the user.
         *
         */
        $scope.submitSignIn = function () {
            var user = this.user;
            var password = this.password;
            this.user = "";
            this.password = "";
            informationFactory.signin(user, password).success(signinSuccessCallback).error(errorCallback);
        };

        /**
         * Changes password for the user.
         *
         * Parameters are sent with angluarjs ng-model="password", ng-model="password1" and ng-model="password2"
         *
         * @ng-model-param password  The current password.
         * @ng-model-param password1 New password.
         * @ng-model-param password2 New password.
         *
         */
        $scope.submitChangePassword = function () {
            var password = this.password;
            var password1 = this.password1;
            var password2 = this.password2;
            this.password = "";
            this.password1 = "";
            this.password2 = "";
            informationFactory.changepasswd(password, password1, password2).success(changepasswdSuccessCallback).error(errorCallback);
        };

        /**
         * Invites a new user to the application.
         *
         * Parameters are sent with angluarjs ng-model="forename", ng-model="surname" and ng-model="email"
         *
         * @ng-model-param forename  First name
         * @ng-model-param surname   Last name
         * @ng-model-param email     E-mail where the invite should be sent.
         *
         */
        $scope.submitInvite = function () {
            var forename = this.forename;
            var surname = this.surname;
            var email = this.email;
            this.forename = "";
            this.surname = "";
            this.email = "";
            informationFactory.invite(forename, surname, email, this.invite_prop.value).success(inviteSuccessCallback).error(errorCallback);
        };

        /**
         * Will close the modal window for signing in.
         *
         * Sets the angluarjs ng-modal parameters user and password to empty.
         */
        $scope.closeSigning = function () {
            this.user = "";
            this.password = "";
            $('#modalSignin').modal('hide');
        };

        /**
         * Will show the modal window for signing in a user.
         */
        $scope.signin = function () {
            $('#modalSignin').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        /**
         * Will show the modal window for changing password.
         */
        $scope.changePassword = function () {
            $('#modalChangePassword').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        /**
         * Will close the modal window for changeing password.
         * Sets the angluarjs ng-modal parameters password, password1 and password2 to empty.
         */
        $scope.closeChangePassword = function () {
            this.password = "";
            this.password1 = "";
            this.password2 = "";
            $('#modalSignin').modal('hide');
        };

        /**
         * Will show the modal window for inviteing users.
         */
        $scope.invite = function () {
            $('#modalInvite').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        /**
         * Will list all users in the user administration.
         */
        $scope.adminUsers = function () {
            informationFactory.adminUsers().success(adminUsersSuccessCallback).error(errorCallback);
        };


        $scope.openUploadImageWindow = function () {
            $('#modalUploadImages').modal('show')
        };


        $scope.closeUploadImages = function () {
            $('#modalUploadImages').modal('hide')
        };


        /**
         * Deletes a user.
         * @param email The e-mail for a user.
         */
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

        /**
         * Changes the administration flag for a users.
         *
         * Parameters are sent with angluarjs ng-model="admin"
         *
         * @ng-model-param admin  1 = user becomes administrator, 0 = user is no longer administrator.
         *
         * @param email The e-mail for a user.
         */
        $scope.changeUserAdmin = function (email) {
            var admin = -1;
            if (this.admin == true) {
                admin = 1;
            } else {
                admin = 0;
            }
            informationFactory.changeUserAdmin(email, admin).success(changeUserAdminSuccessCallback).error(errorCallback);
        };

        /**
         * Changes the valid flag for a users.
         *
         * Parameters are sent with angluarjs ng-model="valid"
         *
         * @ng-model-param admin  1 = user is valid, 0 = user is banned.
         *
         * @param email The e-mail for a user.
         */
        $scope.changeUserValid = function (email, valid) {
            valid = -1;
            if (this.valid == true) {
                valid = 1;
            } else {
                valid = 0;
            }
            informationFactory.changeUserValid(email, valid).success(changeUserValidSuccessCallback).error(errorCallback);
        };

        /**
         * Will show the modal window for changing password.
         */
        $scope.changePassword = function () {
            $('#modalChangePassword').modal('show');
            //informationFactory.signin().success(signinSuccessCallback).error(errorCallback);
        };

        /**
         * Signs out the current user.
         */
        $scope.signout = function () {
            informationFactory.signout().success(signoutSuccessCallback).error(errorCallback);
        };

        /**
         * Handles the response from the application server when the menu file has been retrieved.
         * @param data      The contect of the menu file.
         * @param status    Not used
         */
        var getMenuFileSuccessCallback = function (data, status) {
            $scope.editFile($scope.menu.editmenu, "menu", "You can edit the menu on this page.", data);
            $scope.$apply();
        };

        /**
         * Handles the response from the application server when the custom css file has been retrieved.
         * @param data      The contect of the css file.
         * @param status    Not used
         */
        var getCSSFileSuccessCallback = function (data, status) {
            $scope.editFile($scope.menu.css, "css", "Here you can edit your custom css.", data);
            $scope.$apply();
        };

        /**
         * Retrieves the custom css page.
         */
        $scope.editCSS = function () {
            $scope.iframe = false;
            $('#formContainer').height('');
            informationFactory.getFile("css", getCSSFileSuccessCallback, toaster, $scope);
        };

        /**
         * Retrieves the menu file.
         */
        $scope.editMenu = function () {
            $scope.iframe = false;
            $('#formContainer').height('');
            informationFactory.getFile("menu", getMenuFileSuccessCallback, toaster, $scope);
        };

        /**
         * Will setup the gui for editing custom files. For now you can only edit the menu and custom css file.
         *
         * @param header    Header (breadcrum)
         * @param name      css for custom css file and menu for the menu.
         * @param text      Text to be presented above the content.
         * @param filetext  Content of menu or css file.
         */
        $scope.editFile = function (header, name, text, filetext) {
            $scope.edit = false;
            $scope.oldHeadline = $scope.headline;
            $scope.headline = header;
            $scope.configMenu = true;
            $scope.oldAllowedEdit = $scope.allowedEdit;
            $scope.allowedEdit = false;
            $scope.hideSubmenu = true;

            if (name == "css"){
                $scope.information = text +
                    '<form action="/savefile" class="form" role="form" method="post">' +
                        '<input type="hidden" id="name" name="name" ng-model="name" value="' + name + '" >' +
                        '<button type="submit" class="btn btn-primary">Save</button>' +
                        '<div class="form-group">' +
                            '<textarea id="filetext" name="filetext" rows="10" cols="100" >' + filetext + '</textarea>' +
                        '</div>' +
                        '<button type="submit" class="btn btn-primary">Save</button>' +
                    '</form>'
            }else if (name == "menu"){
                //TODO Change the static height
                $scope.information = '<iframe frameborder="0" scrolling="yes" src="/static/edit_menu.html" style="height: 350px"> </iframe>'
            }
        };

        /**
         * Will set edit mode depending on the users authorization rules.
         */
        $scope.editPage = function () {
            $scope.edit = $scope.allowedEdit;

        };

    });

    /**
     * Yet to be developed.
     * This is the beginning of a page for administrating the menu.
     */
    app.directive('changeMenuValue', function() {
      return function(scope, element) {
        element.bind('change', function() {
          //element.attr('id')
          //element.val();
        });
      };
    });

    /**
     * Yet to be developed.
     * This is the beginning of a page for administrating the menu.
     */
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

    /**
     * Will fetch and display the menu.
     */
    app.directive('menu', function($http) {
            return {
                restrict: 'A',
                templateUrl: '/static/templateMenu.html',
                link: function(scope, element, attrs) {
                    scope.fetchMenu();
                }

            }

    });

    /**
     * Will display tinymce editor when scope.edit is changed to True.
     * If scope.edit is set to false, the tinymce editor is removed.
     *
     * Will insert the tinymce code into the element:
     * <div edit></div>
     */
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
                                height : 300,
                                selector: "textarea#information",
                                relative_urls: false,
                                plugins: [
                                    "advlist autolink link image lists charmap print preview hr anchor pagebreak spellchecker",
                                    "searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking",
                                    "table contextmenu directionality emoticons template paste textcolor"
                                ],
                                setup: function(editor, url) {
                                    editor.addShortcut('ctrl+s','Save', function() {
                                        scope.savePage(true);
                                        scope.$apply();
                                    });
                                },
                                file_browser_callback: function(field_name, url, type, win) {
                                    if (type === "image") {
                                        scope.$broadcast("listImagesEvent", {"field_name": field_name, "window": win});
                                    }
                                }
                            });
                        } else {
                            element[0].innerHTML="";
                        }
                    });
                }

            }
    });

