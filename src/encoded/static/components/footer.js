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
                    <div class="text">
                        <div class="container">
                            <div id="footer-links">
                                <ul>
                                    <li><a href="/">ENCODE</a></li>
                                    <li><a href="">Contact</a></li>
                                    <li><a href="http://www.stanford.edu/site/terms.html">Terms of Use</a></li>
                                </ul>
                            </div>
                        </div>
                        <div class="container">
                            &copy;2013. <a href="http://www.stanford.edu/">Stanford University</a>.
                            <a href="http://med.stanford.edu/">School of Medicine</a>.
                            <a href="http://genetics.stanford.edu/">Department of Genetics</a>.
                        </div>
                    </div>
                    <div class="container logos">
                        <a class="left" href="http://encodeproject.org/"><img src="/static/img/encode-logo.png" alt="ENCODE" /></a>
                        <a class="right" href="http://www.stanford.edu/"><img src="/static/img/su-logo.png" alt="Stanford University" /></a>
                        <a class="right" href="http://www.ucsc.edu/"><img src="/static/img/ucsc-logo.png" alt="University of California Santa Cruz" /></a>
                    </div>
                </footer>
            );
        }
    });


    return Footer;
});
