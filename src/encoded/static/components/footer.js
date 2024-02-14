import PropTypes from 'prop-types';


/* eslint-disable jsx-a11y/anchor-is-valid */
const Footer = ({ version }, reactContext) => {
    const { session } = reactContext;
    const disabled = !session;
    let userActionRender;

    if (!(session && session['auth.userid'])) {
        userActionRender = <a href="#" data-trigger="login" disabled={disabled}>Sign in / Create account</a>;
    } else {
        userActionRender = <a href="#" data-trigger="logout">Sign out</a>;
    }

    return (
        <footer>
            <div className="container">
                <div className="app-version">{version}</div>
            </div>
            <div className="page-footer">
                <div className="container">
                    <div className="footer-sections">
                        <div className="footer-links-section">
                            <ul className="footer-links">
                                <li><a href="/help/citing-encode">Citing ENCODE</a></li>
                                <li><a href="https://www.stanford.edu/site/privacy/">Privacy</a></li>
                                <li><a href="mailto:encode-help@lists.stanford.edu">Contact</a></li>
                            </ul>
                            <ul className="footer-links">
                                <li id="user-actions-footer">{userActionRender}</li>
                            </ul>
                        </div>
                        <div className="footer-logos-section">
                            <ul className="footer-logos">
                                <li><a href="/"><img src="/static/img/encode-logo-small-2x.png" alt="ENCODE" id="encode-logo" height="45px" width="78px" /></a></li>
                                <li><a href="http://www.stanford.edu"><img src="/static/img/su-logo-white-2x.png" alt="Stanford University" id="su-logo" width="105px" height="49px" /></a></li>
                                <li><a href="https://creativecommons.org/licenses/by/4.0/"><img src="/static/img/creative-commons-logo.png" alt="Creative Commons" id="cc-logo" /></a></li>
                            </ul>
                        </div>
                    </div>
                    <p className="copy-notice">&copy;{new Date().getFullYear()} Stanford University</p>
                </div>
            </div>
        </footer>
    );
};
/* eslint-enable jsx-a11y/anchor-is-valid */

Footer.contextTypes = {
    session: PropTypes.object,
};

Footer.propTypes = {
    version: PropTypes.string, // App version number
};

Footer.defaultProps = {
    version: '',
};

export default Footer;
