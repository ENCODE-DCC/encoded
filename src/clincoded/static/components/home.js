'use strict';
var React = require('react');
var globals = require('./globals');

var SignIn = module.exports.SignIn = React.createClass({
    render: function() {
        var hidden = !this.props.session || this.props.session['auth.userid'];
        var disabled = !this.props.loadingComplete;
        return (
            <div id="signin-box" className="col-sm-3" hidden={hidden}>
                <h4>Data Providers</h4>
                <a href="" disabled={disabled} data-trigger="login" className="signin-button btn btn-large btn-success">Sign In</a>
                <p>No access? <a href='mailto:clingen-helpdesk@lists.stanford.edu'>Request an account</a>.</p>
                <p>Authentication by <a href="http://www.mozilla.org/en-US/persona/" target="_blank">Mozilla Persona</a>.</p>
            </div>
        );
    }
});

var Home = module.exports.Home = React.createClass({
    render: function() {
        var hidden = !this.props.session || this.props.session['auth.userid'];
        return (
            <div>
                <div className="homepage-main-box panel-gray">
                    <div className="row">
                        <div className="col-sm-12">
                            <div className="project-info site-title">
                                <h1>ClinGen Curator Portal</h1>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


globals.content_views.register(Home, 'portal');
