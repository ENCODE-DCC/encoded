/** @jsx React.DOM */
define(['exports', 'react', './globals'],
function (exports, React, globals) {
    'use strict';

    var SignIn = exports.SignIn = React.createClass({
        render: function() {
            var hidden = !this.props.session || this.props.session.persona;
            return (
                <div id="signin-box" className="span3" hidden={hidden}>
                    <h4>Data Providers</h4>       
                    <a href="" data-trigger="login" className="signin-button btn btn-large btn-success">Sign In</a>
                    <p>No access? <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>.</p>
                    <p>Authentication by <a href="http://www.mozilla.org/en-US/persona/" target="_blank">Mozilla Persona</a>.</p>
                </div>
            );
        }
    });


    var Home = exports.Home = React.createClass({
        render: function() {
            return (
                <div className="homepage-main-box panel-gray">
                    <div className="row">
                        <div className="project-info home-panel-left span7">
                            <h1>ENCODE</h1>
                            <h2>The Encyclopedia of DNA Elements</h2>
                        </div>
                        <SignIn session={this.props.session} />
                    </div>
                </div>
            );
        }
    });


    globals.content_views.register(Home, 'portal');
    return exports;
});
