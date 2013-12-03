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
            }
        };
    });

    //Controller which will be executed when the web page is loaded
    app.controller('InformationCtrl', function ($scope, informationFactory, toaster) {

        //Variables which will be accessible in index.mako
        $scope.information = "Test page";
        $scope.edit = false;
        $scope.page = "";
        $scope.allowedEdit = true;
        $scope.allowConfig = true;
        $scope.headline = "";
        $scope.authenticated = true;

        var getInformationSuccessCallback = function (data, status, headers, config) {
            $scope.information = data;
            $scope.edit = false;
            //toaster.pop('success', "Notification", "successfully made a Rest request");
        };

        var saveInformationSuccessCallback = function (data, status, headers, config) {
            $scope.information = data;
            $scope.edit = false;
            toaster.pop('success', "Notification", "Successfully saved the page!");
        };


        var errorCallback = function (data, status, headers, config) {
            toaster.pop('error', "Notification", data["ExceptionMessage"]);
        };

        $scope.getInformationFromServer = function (page, name) {
            if (page != "") {
                $scope.headline=name;
                $scope.page = page;
                informationFactory.getInformation(page).success(getInformationSuccessCallback).error(errorCallback);
            }
        };

        $scope.savePage = function () {
            //$http.get('/authedit').success(function(data) {
            //  $scope.allowedEdit = data;
            //});
            if ($scope.allowedEdit) {
                informationFactory.saveInformation($scope.page, tinymce.activeEditor.getContent()).success(saveInformationSuccessCallback).error(errorCallback);
            }
        };

        $scope.editPage = function () {
            //$http.get('/authedit').success(function(data) {
            //  $scope.allowedEdit = data;
            //});
            if ($scope.allowedEdit) {
                $scope.edit = true;
            } else {
                $scope.edit = false;
            }

        };
    });


    app.directive('menu', function($http) {
            return {
                restrict: 'A',
                templateUrl: '/static/templateMenu.html',
                link: function(scope, element, attrs) {
                    $http.get('/menu').success(function(data) {
                        try {
                            scope.getInformationFromServer(data.left[0].submit, data.left[0].name);
                        } catch(e) {
                            try {
                                scope.getInformationFromServer(data.right[0].submit, data.left[0].name);
                            } catch(e) {

                            }
                        }
                        scope.menu=data;
                    });
                }

            }

    });

    app.directive('edit', function($http) {
            return {
                restrict: 'A',
                //template: '<textarea id="information" name="information" class="information" ng-show="edit == true" style="width:100%">{{information}}</textarea>',
                link: function(scope, element, attrs) {
                    //$http.get('/authedit').success(function(data) {
                    //  $scope.allowedEdit = data;
                    //});
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

