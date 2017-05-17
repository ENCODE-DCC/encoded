import React from 'react';
import PropTypes from 'prop-types';
import globals from './globals';


const Error = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'panel-gray');
    return (
        <div className={itemClass}>
            <h1>{context.title}</h1>
            <p>{context.description}</p>
        </div>
    );
};

Error.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.content_views.register(Error, 'Error');


const HTTPNotFound = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'panel-gray');
    return (
        <div className={itemClass}>
            <div className="row">
                <div className="col-sm-12">
                    <h1>Not found</h1>
                    <p>The page could not be found. Please check the URL or enter a search term like <em>skin</em>, <em>ChIP-seq</em>, or <em>CTCF</em> in the toolbar above.</p>
                </div>
            </div>
        </div>
    );
};

HTTPNotFound.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.content_views.register(HTTPNotFound, 'HTTPNotFound');


class HTTPForbidden extends React.Component {
    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'panel-gray');
        const loggedIn = this.context.session && this.context.session['auth.userid'];
        return (
            <div className={itemClass}>
                <div className="row">
                    <div className="col-sm-12">
                        <h1>Not available</h1>
                        {loggedIn ? <p>Your account is not allowed to view this page.</p> : <p>Please sign in to view this page.</p>}
                        {loggedIn ? null : <p>Or <a href="mailto:encode-help@lists.stanford.edu">Request an account.</a></p>}
                    </div>
                </div>
            </div>
        );
    }
}

HTTPForbidden.propTypes = {
    context: PropTypes.object.isRequired,
};

HTTPForbidden.contextTypes = {
    session: PropTypes.object,
};

globals.content_views.register(HTTPForbidden, 'HTTPForbidden');


const LoginDenied = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'panel-gray');
    return (
        <div className={itemClass}>
            <div className="row">
                <div className="col-sm-12">
                    <h2>Our Apologies!</h2>
                    <p>The email address you have provided us does not match any user of the ENCODE Portal.</p>
                    <p>As you know, we have recently changed our login system.</p>

                    <p>The ENCODE Portal now uses a variety of common identity providers to verify you are who say you are.<br />
                        The email address you use as your &ldquot;id&rdquot; must match exactly the email address in our system.</p>

                    <p>Please be aware that login access (to unreleased data) is available only to ENCODE Consortium members.</p>
                    <p>Please contact <a href="mailto:encode-help@lists.stanford.edu">Help Desk</a> if you need an account, or if your old account is not working.</p>
                    <p><a href="http://www.stanford.edu/site/terms.html">Terms and Conditions</a> &emsp; <a href="https://www.encodeproject.org/privacy-policy/">Privacy Policy</a></p>
                </div>
            </div>
        </div>
    );
};

LoginDenied.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.content_views.register(LoginDenied, 'LoginDenied');


const RenderingError = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'panel-gray');
    return (
        <div className={itemClass}>
            <h1>{context.title}</h1>
            <p>{context.description}</p>
            <pre>{context.detail}</pre>
        </div>
    );
};

RenderingError.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.content_views.register(RenderingError, 'RenderingError');
