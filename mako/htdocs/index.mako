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

<%block name="script">
    <!-- Add more script imports here! -->
    ${parent.script()}
     <script type="text/javascript" src="/static/tinymce/tinymce.min.js"></script>
     <script type="text/javascript" src="/static/tinymce/jquery.tinymce.min.js"></script>

</%block>


<%block name="css">
    <!-- Add more css imports here! -->
    <link rel="stylesheet" type="text/css" href="/static/dirg.css">
    ${parent.script()}
</%block>

<%block name="title">
    My test application
    ${parent.title()}
</%block>

<%block name="header">
    ${parent.header()}
</%block>

<%block name="headline">
    <div ng-controller="InformationCtrl">
    <img class="umulogo" src="/static/umu.png" /><span class="logotext">Distributed Identity Research Group</span>

    <nav class="navbar navbar-default" role="navigation">
      <!-- Brand and toggle get grouped for better mobile display -->
    <div menu></div>
    </nav>
    <div class="page-header">{{headline}}</div>
</%block>


<%block name="body">
    <div editmenu></div>
    <div class="glyphicon glyphicon-pencil editpage" ng-show="edit == false && allowedEdit == true && authenticated == true" ng-click="editPage();"></div>
    <div class="glyphicon glyphicon-floppy-save editpage" ng-show="edit == true && allowedEdit == true && authenticated == true"  ng-click="savePage();"></div>

    <div class="information" ng-show="edit == false" ng-bind-html-unsafe="information"></div>

    <br>
    <div edit></div>

    <!-- Modal sign in-->
    <div class="modal fade" id="modalSignin" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
                <h4 class="modal-title" id="myModalLabel">Sign in</h4>
            </div>
          <div class="modal-body">
            <select ng-model="prop.value" ng-click="setAuthMethod();" ng-options="v.type as v.name for v in prop.values"></select>
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
            <form action="spverify" method="post" ng-show="authMethod == 'sp'">
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
      <div class="modal-dialog">
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
              <div class="form-group" ng-show="inviteType == 'idp_new' || inviteType == 'password_new'">
                <label class="sr-only" for="forename">Forename</label>
                <input type="text" class="form-control" ng-model="forename" id="forename" name="forename" placeholder="Enter forename">
              </div>
              <div class="form-group"ng-show="inviteType == 'idp_new' || inviteType == 'idp_new'">
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
            <button type="button" class="btn btn-default close" data-dismiss="modal">Cancel</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

    <!-- Modal change password-->
    <div class="modal fade" id="modalChangePassword" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
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
            <button type="button" class="btn btn-default close" data-dismiss="modal">Cancel</button>
          </div>
        </div><!-- /.modal-content -->
      </div><!-- /.modal-dialog -->
    </div><!-- /.modal -->

</%block>

<%block name="footer">
    </div>
    <script type="text/javascript" src="/static/information.js"></script>

    ${parent.footer()}
</%block>