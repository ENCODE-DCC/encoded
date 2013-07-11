/** @jsx React.DOM */
define(['exports', 'react', 'globals'],
function (home, React, globals) {
    'use strict';

    var SignIn = home.SignIn = React.createClass({
        render: function() {
            var hidden = !this.props.session || this.props.session.persona;
            return (
                <div id="signin-box" class="span3" hidden={hidden}>
                    <h4>Data Providers</h4>       
                    <a href="" data-trigger="login" class="signin-button btn btn-large btn-success">Sign In</a>
                    <p>No access? <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>.</p>
                    <p>Authentication by <a href="http://www.mozilla.org/en-US/persona/" target="_blank">Mozilla Persona</a>.</p>
                </div>
            );
        }
    });


    var Home = home.Home = React.createClass({
        render: function() {
            return (
                <div class="homepage-main-box panel-gray">
                    <div class="row">
                        <div class="project-info home-panel-left span7">
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
    return home;
});
