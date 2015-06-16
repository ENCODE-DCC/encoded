'use strict';
var React = require('react');
var jQuery = require('jquery');
var bootstrap = require('bootstrap');
//var navbar = require('./navbar');
var $ = jQuery;
var jsonScriptEscape = require('../libs/jsonScriptEscape');
var url = require('url');

//var Navbar = navbar.Navbar;

var routes = {
    'curator': require('./curator').Curator
};


var portal = {
    portal_title: 'ClinGen',
    global_sections: [
        {id: 'curator', title: 'Curator', url: '/curator'},
        {id: 'menu2', title: 'Menu 2', url: '/menu2'},
        {id: 'menu3', title: 'Menu 3', url: '/menu3'},
        {id: 'menu4', title: 'Menu 4', url: '/menu4'}
    ]
};


var App = module.exports = React.createClass({
    render: function() {
        var content;
        var context = this.props.context;
        var href_url = url.parse(this.props.href);

        var canonical = this.props.href;
        if (context.canonical_uri) {
            if (href_url.host) {
                canonical = (href_url.protocol || '') + '//' + href_url.host + context.canonical_uri;
            } else {
                canonical = context.canonical_uri;
            }
        }

        return (
            <html lang="en">
                <head>
                    <meta charSet="utf-8" />
                    <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <title>ClinGen</title>
                    <link rel="canonical" href={canonical} />
                    <script data-prop-name="inline" dangerouslySetInnerHTML={{__html: this.props.inline}}></script>
                    <link rel="stylesheet" href="/static/css/style.css" />
                    <script src="/static/build/bundle.js" async defer></script>
                </head>
                <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <script data-prop-name="context" type="application/ld+json" dangerouslySetInnerHTML={{
                        __html: '\n\n' + jsonScriptEscape(JSON.stringify(this.props.context)) + '\n\n'
                    }}></script>
                    <div>
                        <Header />
                    </div>
                </body>
            </html>
        );
    },

    statics: {
        getRenderedProps: function (document) {
            var props = {};
            // Ensure the initial render is exactly the same
            props.href = document.querySelector('link[rel="canonical"]').href;
            var script_props = document.querySelectorAll('script[data-prop-name]');
            for (var i = 0; i < script_props.length; i++) {
                var elem = script_props[i];
                var value = elem.text;
                var elem_type = elem.getAttribute('type') || '';
                if (elem_type == 'application/json' || elem_type.slice(-5) == '+json') {
                    value = JSON.parse(value);
                }
                props[elem.getAttribute('data-prop-name')] = value;
            }
            return props;
        }
    }
});


var Header = React.createClass({
    render: function() {
        return (
            <header className="site-header">
            </header>
        );
    }
});
