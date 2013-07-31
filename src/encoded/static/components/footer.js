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
					<div class="container">
						<div id="footer-links">
							<ul>
								<li><a href="/">ENCODE</a></li>
								<li><a href="">Contact</a></li>
								<li><a href="http://www.stanford.edu/site/terms.html">Terms of Use</a></li>
							</ul>
						</div>
						<div id="footer-logos">
							<ul>
								<li><a href="http://www.stanford.edu"><img src="/static/img/su-logo-white.png" alt="Stanford University" id="su-logo" /></a></li>
								<li><a href="http://med.stanford.edu/"><img src="/static/img/som-logo-red.png" alt="Stanford University School of Medicine" id="som-logo" /></a></li>
								<li>&copy;2013. Stanford University.</li>
							</ul>
						</div>
					</div>
                </footer>
            );
        }
    });


    return Footer;
});
