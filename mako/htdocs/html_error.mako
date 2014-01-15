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
    <img class="umulogo" src="/static/logo.png" /><span class="logotext">Distributed Identity Research Group</span>
</%block>


<%block name="body">
    <div class="verification_message">
        <div class="errormessage">${errormessage}</div>
        <br><br>
        <a href="/">Please click here to go to the home page.</a>
    </div>

</%block>

<%block name="footer">
    ${parent.footer()}
</%block>