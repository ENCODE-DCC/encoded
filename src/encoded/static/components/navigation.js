import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Navbar, Nav, NavItem } from '../libs/bootstrap/navbar';
import { DropdownMenu, DropdownMenuSep } from '../libs/bootstrap/dropdown-menu';
import { productionHost } from './globals';


export default class Navigation extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Set initial React state.
        this.state = {
            testWarning: !productionHost[url.parse(context.location_href).hostname],
            openDropdown: '',
        };

        // Bind this to non-React methods.
        this.handleClickWarning = this.handleClickWarning.bind(this);
        this.documentClickHandler = this.documentClickHandler.bind(this);
        this.dropdownClick = this.dropdownClick.bind(this);
    }

    // Initialize current React component context for others to inherit.
    getChildContext() {
        return {
            openDropdown: this.state.openDropdown,
            dropdownClick: this.dropdownClick,
        };
    }

    componentDidMount() {
        // Add a click handler to the DOM document -- the entire page
        document.addEventListener('click', this.documentClickHandler);
    }

    componentWillUnmount() {
        // Remove the DOM document click handler now that the DropdownButton is going away.
        document.removeEventListener('click', this.documentClickHandler);
    }

    documentClickHandler() {
        // A click outside the DropdownButton closes the dropdown
        this.setState({ openDropdown: '' });
    }

    dropdownClick(dropdownId, e) {
        // After clicking the dropdown trigger button, don't allow the event to bubble to the rest of the DOM.
        e.nativeEvent.stopImmediatePropagation();
        this.setState(prevState => ({
            openDropdown: dropdownId === prevState.openDropdown ? '' : dropdownId,
        }));
    }

    handleClickWarning(e) {
        // Handle a click in the close box of the test-data warning
        e.preventDefault();
        e.stopPropagation();

        // Remove the warning banner because the user clicked the close icon
        this.setState({ testWarning: false });

        // If collection with .sticky-header on page, jiggle scroll position
        // to force the sticky header to jump to the top of the page.
        const hdrs = document.getElementsByClassName('sticky-header');
        if (hdrs.length) {
            window.scrollBy(0, -1);
            window.scrollBy(0, 1);
        }
    }

    render() {
        const portal = this.context.portal;
        return (
            <div id="navbar" className="navbar navbar-fixed-top navbar-inverse">
                <div className="container">
                    <Navbar brand={portal.portal_title} brandlink="/" label="main" navClasses="navbar-main">
                        <GlobalSections />
                        <UserActions />
                        {this.props.isHomePage ? null : <ContextActions />}
                        <Search />
                    </Navbar>
                </div>
                {this.state.testWarning ?
                    <div className="test-warning">
                        <div className="container">
                            <p>
                                The data displayed on this page is not official and only for testing purposes.
                                <button className="test-warning-close icon icon-times-circle-o" onClick={this.handleClickWarning}>
                                    <span className="sr-only">Close test warning banner</span>
                                </button>
                            </p>
                        </div>
                    </div>
                : null}
            </div>
        );
    }
}

Navigation.propTypes = {
    isHomePage: PropTypes.bool, // True if current page is home page
};

Navigation.defaultProps = {
    isHomePage: false,
};

Navigation.contextTypes = {
    location_href: PropTypes.string,
    portal: PropTypes.object,
};

Navigation.childContextTypes = {
    openDropdown: PropTypes.string, // Identifies dropdown currently dropped down; '' if none
    dropdownClick: PropTypes.func, // Called when a dropdown title gets clicked
};


// Main navigation menus
const GlobalSections = (props, context) => {
    const actions = context.listActionsFor('global_sections').map(action =>
        <NavItem key={action.id} dropdownId={action.id} dropdownTitle={action.title}>
            {action.children ?
                <DropdownMenu label={action.id}>
                    {action.children.map((childAction) => {
                        // Render any separators in the dropdown
                        if (childAction.id.substring(0, 4) === 'sep-') {
                            return <DropdownMenuSep key={childAction.id} />;
                        }

                        // Render any regular linked items in the dropdown
                        return (
                            <a href={childAction.url || ''} key={childAction.id}>
                                {childAction.title}
                            </a>
                        );
                    })}
                </DropdownMenu>
            : null}
        </NavItem>
    );
    return <Nav>{actions}</Nav>;
};

GlobalSections.contextTypes = {
    listActionsFor: PropTypes.func.isRequired,
};


// Context actions: mainly for editing the current object
const ContextActions = (props, context) => {
    const actions = context.listActionsFor('context').map(action =>
        <a href={action.href} key={action.name}>
            <i className="icon icon-pencil" /> {action.title}
        </a>
    );

    // No action menu
    if (actions.length === 0) {
        return null;
    }

    // Action menu with editing dropdown menu
    if (actions.length > 1) {
        return (
            <Nav right>
                <NavItem dropdownId="context" dropdownTitle={<i className="icon icon-gear" />}>
                    <DropdownMenu label="context">
                        {actions}
                    </DropdownMenu>
                </NavItem>
            </Nav>
        );
    }

    // Action menu without a dropdown menu
    return <Nav right><NavItem>{actions}</NavItem></Nav>;
};

ContextActions.contextTypes = {
    listActionsFor: PropTypes.func,
};


const Search = (props, context) => {
    const id = url.parse(context.location_href, true);
    const searchTerm = id.query.searchTerm || '';
    return (
        <form className="navbar-form navbar-right" action="/search/">
            <div className="search-wrapper">
                <input
                    className="form-control search-query"
                    id="navbar-search"
                    type="text"
                    placeholder="Search..."
                    name="searchTerm"
                    defaultValue={searchTerm}
                    key={searchTerm}
                />
            </div>
        </form>
    );
};

Search.contextTypes = {
    location_href: PropTypes.string,
};


const UserActions = (props, context) => {
    const sessionProperties = context.session_properties;
    if (!sessionProperties['auth.userid']) {
        // Logged out, so no user menu at all
        return null;
    }
    const actions = context.listActionsFor('user').map(action =>
        <a href={action.href || ''} key={action.id} data-bypass={action.bypass} data-trigger={action.trigger}>
            {action.title}
        </a>
    );
    const user = sessionProperties.user;
    const fullname = (user && user.title) || 'unknown';
    return (
        <Nav right>
            <NavItem dropdownId="useractions" dropdownTitle={fullname}>
                <DropdownMenu label="useractions">
                    {actions}
                </DropdownMenu>
            </NavItem>
        </Nav>
    );
};

UserActions.contextTypes = {
    listActionsFor: PropTypes.func,
    session_properties: PropTypes.object,
};


// Display breadcrumbs with contents given in 'crumbs' object.
// Each crumb in the crumbs array: {
//     id: Title string to display in each breadcrumb. If falsy, does not get included, not even as an empty breadcrumb
//     query: query string property and value, or null to display unlinked id
//     uri: Alternative to 'query' property. Specify the complete URI instead of accreting query string variables
//     tip: Text to display as part of uri tooltip.
//     wholeTip: Alternative to 'tip' property. The complete tooltip to display
// }
const Breadcrumbs = (props) => {
    let accretingQuery = '';
    let accretingTip = '';

    // Get an array of just the crumbs with something in their id
    const crumbs = _.filter(props.crumbs, crumb => crumb.id);
    const rootTitle = crumbs[0].id;

    return (
        <ol className="breadcrumb">
            {crumbs.map((crumb, i) => {
                // Build up the query string if not specified completely
                if (!crumb.uri) {
                    accretingQuery += crumb.query ? `&${crumb.query}` : '';
                }

                // Build up tooltip if not specified completely
                if (!crumb.wholeTip) {
                    accretingTip += crumb.tip ? (accretingTip.length ? ' and ' : '') + crumb.tip : '';
                }

                // Render the breadcrumbs
                return (
                    <li key={i}>
                        {(crumb.query || crumb.uri) ?
                            <a
                                href={crumb.uri ? crumb.uri : props.root + accretingQuery}
                                title={crumb.wholeTip ? crumb.wholeTip : `Search for ${accretingTip} in ${rootTitle}`}
                            >
                                {crumb.id}
                            </a>
                        : <span>{crumb.id}</span>}
                    </li>
                );
            })}
        </ol>
    );
};

Breadcrumbs.propTypes = {
    root: PropTypes.string, // Root URI for searches
    crumbs: PropTypes.arrayOf(PropTypes.object).isRequired, // Object with breadcrumb contents
};
