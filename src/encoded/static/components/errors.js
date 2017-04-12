'use strict';
var React = require('react');
import PropTypes from 'prop-types';
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
        session: PropTypes.object
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
                        <h2>Our Apologies!</h2>
                        <p>The email address you have provided us does not match any user of the ENCODE Portal.</p>
                        <p>As you know, we have recently changed our login system.</p>

                        <p>The ENCODE Portal now uses a variety of common identity providers to verify you are who say you are.<br/>
                           The email address you use as your "id" must match exactly the email address in our system.</p>

                        <p>Please be aware that login access (to unreleased data) is available only to ENCODE Consortium members.</p>
                        <p>Please contact <a href='mailto:encode-help@lists.stanford.edu'>Help Desk</a> if you need an account, or if your old account is not working.</p>
                        <p><a href='http://www.stanford.edu/site/terms.html'>Terms and Conditions</a> &emsp; <a href='https://www.encodeproject.org/privacy-policy/'>Privacy Policy</a></p>
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
