// brazenly ripped from pyramid_persona templates/persona.js then wrapped in require
define(['exports', 'jquery', 'underscore', 'backbone', 'backbone.hal', 'assert'],
function login(exports, $, _, Backbone, HAL, assert) {


    $('#signin').click(function() { navigator.id.request(); return false;});

    $('#signout').click(function() { navigator.id.logout(); return false;});

}