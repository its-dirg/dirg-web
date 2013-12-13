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
</%block>


<%block name="css">
    <!-- Add more css imports here! -->
    <link rel="stylesheet" type="text/css" href="/static/dirg.css">
    ${parent.script()}
</%block>

<%block name="title">
    E-mail verification
    ${parent.title()}
</%block>

<%block name="header">
    ${parent.header()}
</%block>

<%block name="headline">
    <img class="umulogo" src="/static/umu.png" /><span class="logotext">Distributed Identity Research Group</span>
</%block>


<%block name="body">

    % if type == "none":
        <div class="verification_message">
            ${verification_message}
        <br><br>
        <a href="/">Please click here to go to the home page.</a>
    </div>

    % endif
    % if type == "idp":

        <div class="verification_form">
            Please enter the e-mail address registered for you.
            <form action="/spverify" class="form">
              <input type="hidden" id="verify" name="verify" value="true">
                <input type="hidden" id="tag" name="tag" value="${tag}">
              <div class="form-group">
                <label class="sr-only" for="user">Invite e-mail</label>
                <input type="text" class="form-control" id="email" name="email" placeholder="Enter e-mail">
              </div>
              <div class="form-actions">
                  <div class="pull-right">
                    <button type="submit" class="btn btn-primary" >Verify</button>
                  </div>
              </div>
            </form>
        </div>
    % endif
    % if type == "password":
        <form action="/spverify" class="form">
          <input type="hidden" id="verify" name="verify" value="true">
          <div class="form-group">
            <label class="sr-only" for="user">Invite e-mail</label>
            <input type="text" class="form-control" id="email" name="email" placeholder="Enter e-mail">
          </div>
          <div class="form-group">
            <label class="sr-only" for="user">Password</label>
            <input type="text" class="form-control" id="password1" name="password1" placeholder="Enter password">
            <input type="text" class="form-control" id="password2" name="password2" placeholder="Enter password again">
          </div>
          <button type="submit" class="btn btn-primary">Verify</button>
        </form>
    % endif

</%block>

<%block name="footer">
    ${parent.footer()}
</%block>