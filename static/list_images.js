/**
 * Created by regu0004 on 07/08/14.
 */

'use strict';

var list_images = angular.module('list_images', []);


list_images.factory('listImagesFactory', function ($http, serviceBasePath) {
    return {
        listImages: function() {
            return $http.get(serviceBasePath + "/listUploadedImages");
        }
    }
});

list_images.controller('ListImagesCtrl', function ($scope, listImagesFactory, toaster) {

    $scope.imageList = [{"DisplayName": "test.txt"}];
    var field_name;
    var window;

    function listAllImagesSuccessfulCallback(data, status, headers, config) {
        $scope.imageList = [];

        var listIndex = -1;
        for (var i = 0; i < data['Images'].length; ++i) {
            if (i % 12 === 0) {
                $scope.imageList.push([]);
                listIndex += 1;
            }
            $scope.imageList[listIndex].push(data['Images'][i]);
        }
    };

    $scope.imageOnClick = function(image_path){
        $("#modalListImages").modal('hide');
        //$("#" + field_name).val("/" + image_path);

        var element = window.document.getElementById(field_name);
        element.value = image_path;
        console.log(element);
        $(element).change();
    }

    function errorCallback(data, status, headers, config) {
        toaster.pop('error', "Notification", data["ExceptionMessage"]);
    };

    $scope.$on("listImagesEvent", function (event, args) {
        $("#modalListImages").modal('show');
        field_name = args.field_name;
        window = args.window;
        listImagesFactory.listImages().success(listAllImagesSuccessfulCallback).error(errorCallback);
        $scope.$apply();
    });

});


$('#modalListImages').css('z-index', 66001);

$('#modalListImages').on('shown.bs.modal', function (event) {
    $('.modal-backdrop').css('z-index', 66000);
});
