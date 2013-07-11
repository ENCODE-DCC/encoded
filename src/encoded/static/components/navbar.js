/** @jsx React.DOM */
define(['react', 'mixins'],
function (React, mixins) {
    'use strict';

    // Hide data from NavBarLayout
    var NavBar = React.createClass({
        render: function() {
            var section = this.props.location.pathname.split('/', 2)[1] || '';
            return NavBarLayout({
                portal: this.props.portal,
                section: section,
                session: this.props.session,
                user_actions: this.props.user_actions
            });
        }
    });


    var NavBarLayout = React.createClass({
        mixins: [mixins.RenderLess],

        render: function() {
            console.log('render navbar');
            var portal = this.props.portal;
            var section = this.props.section;
            var session = this.props.session;
            var user_actions = this.props.user_actions;
            return (
                <div class="navbar navbar-fixed-top navbar-inverse">
                    <div class="navbar-inner">
                        <div class="container">
                            <a class="btn btn-navbar" href="" data-toggle="collapse" data-target=".nav-collapse">
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                                <span class="icon-bar"></span>
                            </a>
                            <a class="brand" href="/">{portal.portal_title}</a>
                            <div class="nav-collapse collapse">
                                <GlobalSections global_sections={portal.global_sections} section={section} />
                                <UserActions session={session} user_actions={user_actions} />
                            </div>
                        </div>
                    </div>
                </div>
            );
        }
    });


    var GlobalSections = React.createClass({
        render: function() {
            var section = this.props.section;
            var actions = this.props.global_sections.map(function (action) {
                var className = action['class'] || '';
                if (section == action.id) {
                    className += ' active';
                }
                return (
                    <li class={className} key={action.id}>
                        <a href={action.url}>{action.title}</a>
                    </li>
                );
            });
            return <ul id="global-sections" class="nav">{actions}</ul>;
        }
    });


    var UserActions = React.createClass({
        render: function() {
            var session = this.props.session;
            if (!(session && session.persona)) {
                return (
                    <ul id="user-actions" class="nav pull-right" hidden={!session}>
                        <li><a href="" data-trigger="login" data-id="signin">Sign in</a></li>
                    </ul>
                );
            }
            var actions = this.props.user_actions.map(function (action) {
                return (
                    <li class={action.class} key={action.id}>
                        <a href={action.url || ''} data-bypass={action.bypass} data-trigger={action.trigger}>
                            {action.title}
                        </a>
                    </li>
                );
            });
            var fullname = session.user_properties.first_name + ' ' + session.user_properties.last_name;
            return (
                <ul id="user-actions" class="nav pull-right">
                    <li class="dropdown">
                        <a href="" class="dropdown-toggle" data-toggle="dropdown">{fullname}
                        <b class="caret"></b></a>
                        <ul class="dropdown-menu">
                            {actions}
                        </ul>
                    </li>
                </ul>
            );
        }
    });


    return NavBar;
});
