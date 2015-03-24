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

globals.content_views.register(Error, 'error');


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
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'panel-gray');
        if (!this.props.loadingComplete) return (
            <div className="communicating">
                <div className="loading-spinner"></div>
            </div>
        );
        return (
            <div className={itemClass}>
                <div className="row">
                    <div className="col-sm-12">
                        <h1>Not available</h1>
                        <p>Please sign in to view this page.</p> 
                        <p>Or <a href='mailto:encode-help@lists.stanford.edu'>Request an account.</a></p>
                    </div>
                </div>
            </div>
        );
    }
});

globals.content_views.register(HTTPForbidden, 'HTTPForbidden');


var BlankWhileLoading = module.exports.BlankWhileLoading = function (props) {
    if (!props.loadingComplete) return "";
    return props.context.title;
}

globals.listing_titles.register(BlankWhileLoading, 'HTTPForbidden');


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
