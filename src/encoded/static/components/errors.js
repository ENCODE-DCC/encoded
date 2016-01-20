'use strict';
var React = require('react');
var globals = require('./globals');
var home = require('./home');

var Error = module.exports.Error = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'panel-gray');
        return (
            <div className={itemClass}>
                <h1>{context.title}</h1>
                <p>{context.description}</p>
            </div>
        );
    }
});

globals.content_views.register(Error, 'Error');


var HTTPNotFound = module.exports.HTTPNotFound = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'panel-gray');
        return (
            <div className={itemClass}>
                <div className="row">
                    <div className="col-sm-12">
                        <h1>Not found</h1>
                        <p>The page could not be found. Please check the URL or enter a search term like "skin", "ChIP-seq", or "CTCF" in the toolbar above.</p>
                    </div>
                </div>
            </div>
        );
    }
});

globals.content_views.register(HTTPNotFound, 'HTTPNotFound');


var HTTPForbidden = module.exports.HTTPForbidden = React.createClass({
    contextTypes: {
        session: React.PropTypes.object
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'panel-gray');
        var logged_in = this.context.session && this.context.session['auth.userid'];
        return (
            <div className={itemClass}>
                <div className="row">
                    <div className="col-sm-12">
                        <h1>Not available</h1>
                        {logged_in ? <p>Your account is not allowed to view this page.</p> : <p>Please sign in to view this page.</p>}
                        {logged_in ? null : <p>Or <a href='mailto:encode-help@lists.stanford.edu'>Request an account.</a></p>}
                    </div>
                </div>
            </div>
        );
    }
});

globals.content_views.register(HTTPForbidden, 'HTTPForbidden');


var LoginDenied = module.exports.LoginDenied = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'panel-gray');
        return (
            <div className={itemClass}>
                <div className="row">
                    <div className="col-sm-12">
                        <h1>Login failure</h1>
                        <p>Access is restricted to ENCODE consortium members.</p>
                        <p><a href='mailto:encode-help@lists.stanford.edu'>Request an account</a></p>
                        
                    </div>
                </div>
            </div>
        );
    }
});

globals.content_views.register(LoginDenied, 'LoginDenied');


var RenderingError = module.exports.RenderingError = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'panel-gray');
        return (
            <div className={itemClass}>
                <h1>{context.title}</h1>
                <p>{context.description}</p>
                <pre>{context.detail}</pre>
            </div>
        );
    }
});

globals.content_views.register(RenderingError, 'RenderingError');
