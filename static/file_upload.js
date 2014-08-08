/**
 * Created by regu0004 on 07/08/14.
 */

'use strict';

//Controller which will be executed when the web page is loaded
app.controller('FileUploadCtrl', ['$scope', 'toaster', 'FileUploader', function ($scope, toaster, FileUploader) {
    var acceptedFileTypes = ['.png', '.jpg', '.jpeg'];
    $scope.acceptedFileTypes = acceptedFileTypes.join();

    var uploader = $scope.uploader = new FileUploader({
        url: '/uploadImage',
        method: 'POST',
        queueLimit: 1,
        removeAfterUpload: true,
        autoUpload: true
    });

    uploader.onSuccessItem = function (fileItem, response, status, headers) {
        console.info('onSuccessItem', fileItem, response, status, headers);
        toaster.pop('success', "Notification", response);
        $("#modalUploadImages").modal('hide');
    };

    uploader.onErrorItem = function (fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
        toaster.pop('error', "Notification", response['ExceptionMessage']);
    };

}]);