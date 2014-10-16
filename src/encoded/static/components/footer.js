/** @jsx React.DOM */
'use strict';
var React = require('react');

var Footer = React.createClass({
    shouldComponentUpdate: function (nextProps, nextState) {
        return false;
    },

    render: function() {
        console.log('render footer');
        return (
            <footer id="page-footer" className="page-footer">
                <div className="container">
                    <div className="row">
                        <div className="col-sm-5 col-sm-push-7">
                            <ul className="footer-links">
                                <li><a href="mailto:encode-help@lists.stanford.edu">Contact</a></li>
                                <li><a href="http://www.stanford.edu/site/terms.html">Terms of Use</a></li>
                            </ul>
                            <p className="copy-notice">&copy;{new Date().getFullYear()} Stanford University.</p>
                        </div>
                        
                    <div className="col-sm-7 col-sm-pull-5">
                            <ul className="footer-logos">
                                <li><a href="/"><img src="/static/img/encode-logo-small-2x.png" alt="ENCODE" id="encode-logo" height="45px" width="78px" /></a></li>
                                <li><a href="http://www.ucsc.edu"><img src="/static/img/ucsc-logo-white-alt-2x.png" alt="UC Santa Cruz" id="ucsc-logo" width="107px" height="42px" /></a>
                                </li>
                                <li><a href="http://www.stanford.edu"><img src="/static/img/su-logo-white-2x.png" alt="Stanford University" id="su-logo" width="105px" height="49px" /></a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </footer>
        );
    }
});

module.exports = Footer;
