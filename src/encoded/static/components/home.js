/** @jsx React.DOM */
'use strict';
var React = require('react');
var globals = require('./globals');

var SignIn = module.exports.SignIn = React.createClass({
    render: function() {
        var hidden = !this.props.session || this.props.session.persona;
        var disabled = !this.props.personaReady;
        return (
            <div id="signin-box" className="span3" hidden={hidden}>
                <h4>Data Providers</h4>
                <a href="" disabled={disabled} data-trigger="login" className="signin-button btn btn-large btn-success">Sign In</a>
                <p>No access? <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>.</p>
                <p>Authentication by <a href="http://www.mozilla.org/en-US/persona/" target="_blank">Mozilla Persona</a>.</p>
            </div>
        );
    }
});

var Home = module.exports.Home = React.createClass({
    render: function() {
        var hidden = !this.props.session || this.props.session.persona;
        return (
            <div>
                <div className="homepage-main-box panel-gray">
                    <div className="row">
                        <div className="span12">
                            <div className="project-info site-title">
                                <h1>ENCODE: The Encyclopedia of DNA Elements</h1>
                            </div>
                            <div id="info-box" className="project-info text-panel">
                                <h4>Preview the new ENCODE Portal</h4>
                                <p>Enter a search term like "skin", "ChIP-seq", or "CTCF" or select a data type in the toolbar above.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }
});


globals.content_views.register(Home, 'portal');
