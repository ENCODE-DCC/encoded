/** @jsx React.DOM */
'use strict';

jest.autoMockOff();
jest.mock('jquery');
// Fixes https://github.com/facebook/jest/issues/78
jest.dontMock('underscore');


describe("Server rendering", function () {
    var React;
    var App;
    var document;
    var home_url = "http://localhost/";
    var home = {
        "@id": "/",
        "@type": ["portal"],
        "portal_title": "ENCODE",
        "title": "Home"
    };

    beforeEach(function () {
        React = require('react');
        App = require('..');
        var server_app = <App context={home} href={home_url} />;
        var markup = '<!DOCTYPE html>\n' + React.renderComponentToString(server_app);
        var parser = new DOMParser();
        document = parser.parseFromString(markup, 'text/html');
    });

    it("renders the application to html", function () {
        expect(document.title).toBe(home.portal_title);
    });

    it("mounts the application over the rendered html", function () {
        var props = {};
        props.href = document.querySelector('link[rel="canonical"]').href;
        var script_props = document.querySelectorAll('script[data-prop-name]');
        for (var i = 0; i < script_props.length; i++) {
            var elem = script_props[i];
            props[elem.getAttribute('data-prop-name')] = JSON.parse(elem.text);
        }
        var app = React.renderComponent(App(props), document);
        expect(app.getDOMNode()).toBe(document.documentElement);
    });
});
