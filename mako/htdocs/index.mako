## index.html
<!--
You must install dirg-util to be able to use dirg-base.mako
-->
<%inherit file="base.mako"/>
<!--
This is the content part of the Mako template. This project uses two frameworks:

Bootstrap which supplies graphical components like buttons and icon. It also supports responsive design.
More info at http://getbootstrap.com/

AngularJs which generates html code based on javascript objects. Read more at http://docs.angularjs.org/api/

There is also a javascript based notification library Toaster which uses AngularJS.
Toaster is used for displaying notifications in a nice way.

Please view static/test.js for more example of angular and toaster.
-->
<%block name="meta">
    <!--<meta http-equiv="Content-Security-Policy" content="default-src 'self'"/>-->
</%block>
<%block name="script">

    <!-- Add more script imports here! -->
    ${parent.script()}
     <script type="text/javascript" src="/static/tinymce/tinymce.min.js"></script>
     <script type="text/javascript" src="/static/tinymce/jquery.tinymce.min.js"></script>

</%block>


<%block name="css">
    <!-- Add more css imports here! -->
    <link rel="stylesheet" type="text/css" href="/static/dirg.css">
    <link rel="stylesheet" type="text/css" href="/static/custom.css">
    ${parent.script()}
</%block>

<%block name="title">
    DIRG
    ${parent.title()}
</%block>

<%block name="header">
    ${parent.header()}
</%block>

<%block name="headline">
    <div id="InformationCtrl" ng-controller="InformationCtrl">
    <img class="umulogo" src="/static/logo.png" /><span class="logotext">Distributed Identity Research Group</span>

    <nav class="navbar navbar-default" role="navigation">
      <!-- Brand and toggle get grouped for better mobile display -->
    <div menu></div>
    </nav>
    <div class="page-header">{{headline}}</div>
</%block>


<%block name="body">
    <div editmenu></div>
    <div class="glyphicon glyphicon-pencil editpage" ng-show="edit == false && allowedEdit == true && authenticated == true && iframe==false" ng-click="editPage();"></div>
    <div class="glyphicon glyphicon-floppy-save editpage" ng-show="edit == true && allowedEdit == true && authenticated == true && iframe==false"  ng-click="savePage(false);"></div>
    <div ng-controller="FileUploadCtrl">
        <input type="file" accept="{{acceptedFileTypes}}" nv-file-select uploader="uploader"/>
    </div>

<div ng-show="iframe==true" id="frame_div" class="iframe_div">
    <span data-toggle="tooltip" title="Click to enter fullscreen mode." id="max_icon" class="glyphicon glyphicon-plus-sign show_icon" onclick="max_iframe()"></span>
    <span title="Click to leave fullscreen mode." id="min_icon" class="glyphicon glyphicon-minus-sign hide_icon" onclick="min_iframe()"></span>
    <iframe src="{{iframe_src}}" scrolling="yes" frameborder="0"></iframe>
</div>


<table ng-show="edit == false && iframe==false" class="main">
    <tr>
    <td style="width: 1px;">
        <div class="panel-group" id="accordion" style="padding-top: 15px;" ng-show="hideSubmenu == false">
            <div class="panel panel-default" ng-repeat="element in submenu">
            <div class="panel-heading">
              <h4 class="panel-title" ng-show="element.type == 'static'" >
                <span style="white-space:nowrap;">{{element.name}}&nbsp;</span>
              </h4>
              <h4 class="panel-title" ng-show="element.type == 'collapse_open' || element.type == 'collapse_close'" data-toggle="collapse" href="#{{element.submit}}">
                <span style="white-space:nowrap;">{{element.name}}&nbsp;<span class="glyphicon glyphicon-chevron-down"> </span></span>
              </h4>
            </div>
            <ul id="{{element.submit}}" class="panel-collapse collapse {{element.class}} list-group" >
              <li class="list-group-item" ng-repeat="list_element in element.list"><a ng-click="getInformationFromServer(page, element.submit, list_element.submit);" style="white-space:nowrap;">{{list_element.name}}</a></li>
            </ul>
          </div>
        </div>
    </td>
    <td>
        <div class="information" ng-show="edit == false  && information != ''" ng-bind-html-unsafe="information"></div>
    </td>
     </tr>
</table>
    <br>
    <div edit></div>

    <!-- Modal sign in-->
    <div class="modal fade" id="modalSignin" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true" ng-click="closeSigning()">&times;</button>
                <h4 class="modal-title" id="myModalLabel">Sign in</h4>
            </div>
          <div class="modal-body">
            <select ng-model="prop.value" ng-change="setAuthMethod();" ng-options="v.type as v.name for v in prop.values"></select>
            <form ng-submit="submitSignIn()" class="form" role="form" ng-show="authMethod == 'userpassword'">
              <div class="form-group">
                <label class="sr-only" for="user">User</label>
                <input type="text" class="form-control" ng-model="user" id="user" name="user" placeholder="Enter username">
              </div>
              <div class="form-group">
                <label class="sr-only" for="password">Password</label>
                <input type="password" class="form-control" ng-model="password" id="password" name="password" placeholder="Password">
              </div>
              <button type="submit" class="btn btn-primary">Sign in</button>
            </form>
            <form action="/spverify" method="post" ng-show="authMethod == 'sp'">
              <button type="submit" class="btn btn-primary">Sign in</button>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal" ng-click="closeSigning()">Cancel</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

    <!-- Modal invite user-->
    <div class="modal fade" id="modalInvite" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog" >
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h4 class="modal-title" id="myModalLabel">Invite</h4>
            </div>
          <div class="modal-body">
            <form ng-submit="submitInvite()" class="form" role="form">
              <div class="form-group">
                 <label class="sr-only" for="type">Type</label>
                 <select ng-model="invite_prop.value" ng-click="setInviteType();" id="type" name="type" ng-options="v.type as v.name for v in invite_prop.values"></select>
              </div>
              <div class="form-group" ng-show="inviteType == 'idp_new' || inviteType == 'pass_new'">
                <label class="sr-only" for="forename">Forename</label>
                <input type="text" class="form-control" ng-model="forename" id="forename" name="forename" placeholder="Enter forename">
              </div>
              <div class="form-group"ng-show="inviteType == 'idp_new' || inviteType == 'pass_new'">
                <label class="sr-only" for="surname">Surname</label>
                <input type="text" class="form-control" ng-model="surname" id="surname" name="surname" placeholder="Enter surname">
              </div>
              <div class="form-group">
                <label class="sr-only" for="user">Invite e-mail</label>
                <input type="text" class="form-control" ng-model="email" id="email" name="email" placeholder="Enter e-mail">
              </div>
              <button type="submit" class="btn btn-primary">Invite</button>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Cancel</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

    <!-- Modal change password-->
    <div class="modal fade" id="modalChangePassword" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true" ng-click="closeChangePassword()">&times;</button>
                <h4 class="modal-title" id="myModalLabel">Change password</h4>
            </div>
          <div class="modal-body">
            <form ng-submit="submitChangePassword()" class="form" role="form">
              <div class="form-group">
                <label class="sr-only" for="password">Old password</label>
                <input type="password" class="form-control" ng-model="password" id="password" name="password" placeholder="Enter current password">
              </div>
              <div class="form-group">
                <label class="sr-only" for="password1">New password</label>
                <input type="password" class="form-control" ng-model="password1" id="password1" name="password1" placeholder="Enter new password">
              </div>
              <div class="form-group">
                <label class="sr-only" for="password2">New password again</label>
                <input type="password" class="form-control" ng-model="password2" id="password2" name="password2" placeholder="Enter new password again">
              </div>
              <button type="submit" class="btn btn-primary">Change password</button>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal" ng-click="closeChangePassword()">Cancel</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

    <!-- Administrate users-->
    <div class="modal fade" id="modalAdministrateUsers" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog large">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h4 class="modal-title" id="myModalLabel">Administrate users</h4>
            </div>
          <div class="modal-body">
                <table class="table table-striped">
                    <tr>
                        <th>
                        </th>
                        <th>
                            Name/E-mail
                        </th>
                        <th>
                            Admin
                        </th>
                        <th>
                            Active
                        </th>
                        <th>
                            Verified
                        </th>
                    </tr>
                    <tr ng-repeat="user in users">
                        <td><div ng-click="deleteUser(user.email)" class="glyphicon glyphicon-remove" style="cursor: pointer;" title="Deletes the user."></div></td>
                        <td>
                            {{user.forename}} {{user.surname}}<br>
                            {{user.email}}
                        </td>
                        <td style="vertical-align: middle">
                            <div class="checkbox">
                              <label>
                                <input type="checkbox" ng-model="admin" ng-click="changeUserAdmin(user.email)" ng-checked="user.admin == 1" >
                              </label>
                            </div>
                        </td>
                        <td style="vertical-align: middle">
                            <div class="checkbox">
                              <label>
                                <input type="checkbox" ng-model="valid" ng-click="changeUserValid(user.email, this.checked)" ng-checked="user.valid == 1" >
                              </label>
                            </div>
                        </td>
                        <td style="vertical-align: middle">
                            <div class="checkbox">
                              <label>
                                <input type="checkbox" disabled="disabled" ng-checked="user.verify == 0" >
                              </label>
                            </div>
                        </td>
                    </tr>
                </table>

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

</%block>

<%block name="footer">
    </div>
    <script type="text/javascript" src="/information_init_app_js"></script>
    <script type="text/javascript" src="/static/information.js"></script>
    <script type="text/javascript" src="/static/angular-file-upload.min.js"></script>
    <script type="text/javascript" src="/static/file_upload.js"></script>
    ${parent.footer()}
</%block>