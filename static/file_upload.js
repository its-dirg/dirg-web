/**
 * Created by regu0004 on 07/08/14.
 */

'use strict';

//Controller which will be executed when the web page is loaded
app.controller('FileUploadCtrl', ['$scope', 'toaster', 'FileUploader', function ($scope, toaster, FileUploader) {
    var acceptedFileTypes = ['.png', '.jpg', '.jpeg'];
    $scope.acceptedFileTypes = acceptedFileTypes.join();
    console.log($scope.acceptedFileTypes);


    var uploader = $scope.uploader = new FileUploader({
        url: '/uploadImage',
        method: 'POST',
        queueLimit: 1,
        removeAfterUpload: true,
        autoUpload: true
    });

    uploader.filters.push({
        name: 'FileTypeFilter',
        fn: function (item) {
            var type = '|.' + item.type.slice(item.type.lastIndexOf('/') + 1) + '|';
            var accept = '|' + acceptedFileTypes.join('|') + '|';
            return accept.indexOf(type) !== -1;
        }
    });

    uploader.onWhenAddingFileFailed = function (item /*{File|FileLikeObject}*/, filter, options) {
        console.info('onWhenAddingFileFailed', item, filter, options);
    };
    uploader.onAfterAddingFile = function (fileItem) {
        console.info('onAfterAddingFile', fileItem);
    };
    uploader.onProgressItem = function (fileItem, progress) {
        console.info('onProgressItem', fileItem, progress);
    };
    uploader.onSuccessItem = function (fileItem, response, status, headers) {
        console.info('onSuccessItem', fileItem, response, status, headers);
        console.log('File upload SUCCESS!')
    };
    uploader.onErrorItem = function (fileItem, response, status, headers) {
        console.info('onErrorItem', fileItem, response, status, headers);
        console.log('File upload FAIL!')
    };

    console.info('uploader', uploader);
}]);