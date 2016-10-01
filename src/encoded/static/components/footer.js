'use strict';
var React = require('react');

var Footer = React.createClass({
    contextTypes: {
        session: React.PropTypes.object
    },

    propTypes: {
        version: React.PropTypes.string // App version number
    },

    render: function() {
        var session = this.context.session;
        var disabled = !session;
        var userActionRender;

        if (!(session && session['auth.userid'])) {
            userActionRender = <a href="#" data-trigger="login" disabled={disabled}>Submitter sign-in</a>;
        } else {
            userActionRender = <a href="#" data-trigger="logout">Submitter sign out</a>;
        }
        return (
            <footer id="page-footer">
                <div className="container">
                    <div className="app-version">{this.props.version}</div>
                </div>
                <div className="page-footer">
                    <div className="container">
                        <div className="row">
                            <div className="col-sm-5 col-sm-push-7 col-md-6 col-md-push-6">
                                <ul className="footer-links">
                                    <li><a href="mailto:encode-help@lists.stanford.edu">Contact</a></li>
                                    <li><a href="http://www.stanford.edu/site/terms.html">Terms of Use</a></li>
                                    <li id="user-actions-footer">{userActionRender}</li>
                                </ul>
                                <p className="copy-notice">&copy;{new Date().getFullYear()} Stanford University.</p>
                            </div>

                            <div className="col-sm-7 col-sm-pull-5 col-md-6 col-md-pull-6">
                                <ul className="footer-logos">
                                    <li><a href="/"><img src="/static/img/encode-logo.svg" alt="ENCODE" id="encode-logo" height="45px" width="78px" /></a></li>
                                    <li><a href="http://www.stanford.edu"><img src="/static/img/su-logo-white.svg" alt="Stanford University" id="su-logo" width="105px" height="49px" /></a></li>
                                    <li><a width="150" height="50" href="https://auth0.com/?utm_source=oss&utm_medium=gp&utm_campaign=oss" target="_blank" alt="Single Sign On & Token Based Authentication - Auth0"><img width="150" height="50" alt="JWT Auth for open source projects" src="/static/img/a0-badge-light.png"/></a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }
});

module.exports = Footer;
