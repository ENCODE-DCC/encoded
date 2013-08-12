/** @jsx React.DOM */
define(['react'],
function (React) {
    'use strict';


    var Footer = React.createClass({
        shouldComponentUpdate: function (nextProps, nextState) {
            return false;
        },

        render: function() {
            console.log('render footer');
            return (
                <footer id="page-footer">
                    <div id="footer-top">
                        <div class="container">
                            <a href="http://www.stanford.edu"><img src="/static/img/su-logo.png" alt="Stanford University" id="su-logo" /></a>
                            <a href="http://med.stanford.edu/"><img src="/static/img/som-logo.png" alt="Stanford University School of Medicine" id="som-logo" /></a>
                            <div id="footer-links">
                                <ul>
                                    <li><a href="/">ENCODE</a></li>
                                    <li><a href="">Contact</a></li>
                                    <li><a href="http://www.stanford.edu/site/terms.html">Terms of Use</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    <div id="footer-bottom">
                        <div class="container">
                            &copy;2013. <a href="http://www.stanford.edu/">Stanford University</a>.
                            <a href="http://med.stanford.edu/">School of Medicine</a>.
                            <a href="http://genetics.stanford.edu/">Department of Genetics</a>.
                        </div>
                    </div>
                </footer>
            );
        }
    });


    return Footer;
});
