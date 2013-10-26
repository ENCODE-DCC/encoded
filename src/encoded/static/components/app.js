/** @jsx React.DOM */
define(['jquery', 'react', 'uri', './globals', './mixins', './navbar', './footer'],
function ($, React, URI, globals, mixins, NavBar, Footer) {
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
            var context;
            var location = URI(this.props.href);
            // The initial context is read in from the contextDataElement
            // That element is then kept in sync for easier debugging.
            if (this.props.contextDataElement) {
                context = JSON.parse(this.props.contextDataElement.text);
            } else {
                this.navigate(location.href, {replace: true});
            }
            return {
                context: context,
                errors: [],
                location: location,
                portal: portal,
                session: null,
                user_actions: user_actions
            };
        },

        componentWillReceiveProps: function (nextProps) {
            this.setState({
                location: URI(nextProps.href)
            });
        },

        render: function() {
            console.log('render app');
            var content;
            var context = this.state.context;
            if (context) {
                var ContentView = globals.content_views.lookup(context);
                content = ContentView({
                    context: this.state.context,
                    location: this.state.location,
                    session:this.state.session
                });
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

            return (
                <div id="application" className={appClass} onClick={this.handleClick} onSubmit={this.handleSubmit}>
                    <div id="layout">
                        <NavBar location={this.state.location} portal={this.state.portal} user_actions={this.state.user_actions} session={this.state.session} />
                        <div id="content" className="container">
                            {content}
                        </div>
                        {errors}                        
                        <div id="layout-footer"></div>
                    </div>
                    <Footer />
                </div>
            );
        },

        componentDidUpdate: function () {
            // XXX The templates should be updated to always define an h1.
            $('title').text($('h1, h2').first().text() + ' - ' + $('#navbar .brand').first().text());
        }

    });


    return App;

});
