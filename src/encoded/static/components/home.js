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

var Info = module.exports.Info = React.createClass({
    render: function() {
        return (
            <div className="span3">
            	<div id="info-box" className="text-panel">
					<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas feugiat posuere lorem, id posuere odio commodo at.</p>
					<p>Curabitur in eleifend mauris, ut malesuada tellus. Maecenas facilisis venenatis odio, laoreet tincidunt eros bibendum a. Sed pulvinar justo eu scelerisque ullamcorper. Vivamus eget mollis purus. Maecenas condimentum convallis ante, sit amet tincidunt lacus porta vel.</p>
            	</div>
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
                        <div className="project-info home-panel-left span7">
                            <h1>ENCODE</h1>
                            <h2>The Encyclopedia of DNA Elements</h2>
                        </div>
                        <Info />
                    </div>
                </div>
            </div>
        );
    }
});


globals.content_views.register(Home, 'portal');
