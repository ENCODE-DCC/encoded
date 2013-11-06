/** @jsx React.DOM */
define(['exports', 'react', './globals', './home'],
function (exports, React, globals, home) {
    'use strict';

    var SignIn = home.SignIn;


    var Error = exports.Error = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'panel-gray');
            return (
                <div className={itemClass}>
                    <h1>{context.title}</h1>
                    <p>{context.description}</p>
                </div>
            );
        }
    });

    globals.content_views.register(Error, 'error');


    var LoginDenied = exports.LoginDenied = React.createClass({
        render: function() {
            var context = this.props.context;
            var itemClass = globals.itemClass(context, 'panel-gray');
            return (
                <div className={itemClass}>
                    <div className="row">
                        <div className="span7">
                            <h1>Login failure</h1>
                            <p>Access is restricted to ENCODE consortium members.
                                <a href='mailto:encode-help@lists.stanford.edu'>Request an account</a>
                            </p>
                        </div>
                        <SignIn session={this.props.session} />
                    </div>
                </div>
            );
        }
    });

    globals.content_views.register(LoginDenied, 'LoginDenied');


    return exports;
});
