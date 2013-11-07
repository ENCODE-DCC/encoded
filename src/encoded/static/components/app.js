/** @jsx React.DOM */
define(['react', 'jsonScriptEscape', './globals', './mixins', './navbar', './footer'],
function (React, jsonScriptEscape, globals, mixins, NavBar, Footer) {
    /*jshint devel: true*/
    'use strict';

    var portal = {
        portal_title: 'ENCODE',
        global_sections: [
            {id: 'antibodies', title: 'Antibodies', url: '/antibodies/'},
            {id: 'biosamples', title: 'Biosamples', url: '/biosamples/'},
            {id: 'experiments', title: 'Experiments', url: '/experiments/'},
            {id: 'targets', title: 'Targets', url: '/targets/'}
        ]
    };


    var user_actions = [
        {id: 'signout', title: 'Sign out', trigger: 'logout'}
    ];


    // App is the root component, mounted on document.body.
    // It lives for the entire duration the page is loaded.
    // App maintains state for the
    var App = React.createClass({
        mixins: [mixins.Persona, mixins.HistoryAndTriggers],
        triggers: {
            login: 'triggerLogin',
            logout: 'triggerLogout'
        },

        getInitialState: function() {
            return {
                errors: [],
                portal: portal,
                session: null,
                user_actions: user_actions
            };
        },

        render: function() {
            console.log('render app');
            var content;
            var context = this.props.context;
            if (context) {
                var ContentView = globals.content_views.lookup(context);
                content = this.transferPropsTo(ContentView({
                    personaReady: this.state.personaReady,
                    session: this.state.session
                }));
            }
            var errors = this.state.errors.map(function (error) {
                return <div className="alert alert-error"></div>;
            });

            var appClass;
            if (this.state.communicating) {
                appClass = 'communicating';
            } else {
                appClass = 'done';
            }

            var title = globals.listing_titles.lookup(context)({context: context});
            if (title && title != 'Home') {
                title = title + ' – ' + portal.portal_title;
            } else {
                title = portal.portal_title;
            }

            return (
                <html>
                    <head>
                        <meta charset="utf-8" />
                        <meta http-equiv="content-language" content="en" />
                        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        <title>{title}</title>
                        <link rel="canonical" href={this.props.href} />
                        <link rel="stylesheet" href="/static/css/style.css" />
                        <link rel="stylesheet" href="/static/css/responsive.css" />
                        <script src="/static/build/bundle.js" async={true} defer={true}></script>
                    </head>
                    <body onClick={this.handleClick} onSubmit={this.handleSubmit}>
                        <script data-prop-name="context" type="application/ld+json" dangerouslySetInnerHTML={{
                            __html: jsonScriptEscape(JSON.stringify(this.props.context))
                        }}></script>
                        <div id="slot-application">
                            <div id="application" className={appClass}>
                                <div id="layout">
                                    <NavBar href={this.props.href} portal={this.state.portal}
                                            user_actions={this.state.user_actions} session={this.state.session}
                                            personaReady={this.state.personaReady} />
                                    <div id="content" className="container">
                                        {content}
                                    </div>
                                    {errors}                        
                                    <div id="layout-footer"></div>
                                </div>
                                <Footer />
                            </div>
                        </div>
                    </body>
                </html>
            );
        }

    });


    return App;

});
