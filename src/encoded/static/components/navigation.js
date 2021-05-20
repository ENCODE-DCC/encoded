import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Navbar, Nav, NavItem } from '../libs/ui/navbar';
import { DropdownMenu, DropdownMenuSep } from '../libs/ui/dropdown-menu';
import { CartStatus } from './cart';
import { isProductionHost } from './globals';
import Tooltip from '../libs/ui/tooltip';
import { BrowserFeat } from './browserfeat';
import NavBarMultiSearch from './top_hits/multi/search';

/**
 * Navigation bar home-page button.
 */
class HomeBrand extends React.Component {
    constructor() {
        super();
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.context.navigate('/');
    }

    render() {
        return (
            <button type="button" className="home-brand" onClick={this.handleClick}>
                {this.context.portal.portal_title}
                <span className="sr-only">Home</span>
            </button>
        );
    }
}

HomeBrand.contextTypes = {
    navigate: PropTypes.func,
    portal: PropTypes.object,
};

export default class Navigation extends React.Component {
    constructor(props, context) {
        super(props, context);

        // Set initial React state.
        this.state = {
            /** ID of the currently dropped-down main navigation menu; '' if none */
            openDropdown: '',
            /** True if test warning banner visible; default depends on domain */
            testWarning: !isProductionHost(context.location_href),
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
        document.addEventListener('click', (e) => this.documentClickHandler(e));
    }

    componentWillUnmount() {
        // Remove the DOM document click handler now that the DropdownButton is going away.
        document.removeEventListener('click', (e) => this.documentClickHandler(e));
    }

    /**
     * Handle a click in the close box of the test-data warning.
     * @param {object} e React synthetic event
     */
    handleClickWarning(e) {
        e.preventDefault();
        e.stopPropagation();

        // Remove the warning banner because the user clicked the close icon
        this.setState({ testWarning: false });

        // If collection with .sticky-header on page, jiggle scroll position
        // to force the sticky header to jump to the top of the page.
        const hdrs = document.getElementsByClassName('sticky-header');
        if (hdrs.length > 0) {
            window.scrollBy(0, -1);
            window.scrollBy(0, 1);
        }
    }

    /**
     * A click outside the DropdownButton closes the dropdown.
     */
    documentClickHandler(e) {
        const { className } = e.target;
        // Only close navigation hamburger when user does not click on tooltip icon
        // Note: "toString" is required for hamburger SVG on mobile which does not have a className that is a string
        // Elements with validClassName and validTagName should not close the menu when clicked on
        let validClassName = false;
        if (className) {
            validClassName = (className.toString().indexOf('icon-question-circle') > -1) || (className.toString().indexOf('tooltip-container__trigger') > -1);
        }
        const validTagName = e.target.tagName === 'LI' || e.target.tagName === 'I';
        if (!(validClassName || validTagName)) {
            this.setState({ openDropdown: '' });
        }
    }

    /**
     * Called when the user clicks a main navigation drop-down menu.
     * @param {string} dropdownId ID of the clicked menu, if any
     * @param {object} e React synthetic event
     */
    dropdownClick(dropdownId, e) {
        // Clicks and mouseover actions do not behave the same way (clicks should toggle activation whereas hovering should maintain activation)
        // so depending on the device we want user actions have different results
        // We do enable clicks on non-touch devices so that menus are available by keyboard (tab)
        let activateMenuItem = false;
        const isMobile = BrowserFeat.getBrowserCaps('touchEnabled');
        const dropdownIdIsString = typeof dropdownId === 'string';
        if (e) {
            // After clicking the dropdown trigger button, don't allow the event to bubble to the rest of the DOM.
            e.nativeEvent.stopImmediatePropagation();
            // On touch devices, activate menu item if new one chosen or deactivate menu item if old one chosen
            if (e.type === 'click' && isMobile) {
                activateMenuItem = dropdownId !== this.state.openDropdown;
                this.setState((prevState) => ({
                    openDropdown: ((dropdownId !== prevState.openDropdown) && dropdownIdIsString) ? dropdownId : '',
                }));
            // On non-touch devices, a click functions like a hover would, it only activates and cannot deactivate
            // This is primarily useful for accessibility
            } else if (e.type === 'click') {
                activateMenuItem = true;
                this.setState({
                    openDropdown: (activateMenuItem && dropdownIdIsString) ? dropdownId : '',
                });
            // On non-touch devices, activate menu item on mouseenter or deactivate on mouseleave
            // Note that mouseenter and mouseleave are not available on touch devices
            } else if ((e.type === 'mouseenter' || e.type === 'mouseleave') && !isMobile) {
                // On mousenter, activate menu item
                if (e.type === 'mouseenter') {
                    activateMenuItem = true;
                }
                // On mouseleave, de-activate menu item
                if (e.type === 'mouseleave') {
                    activateMenuItem = false;
                }
                this.setState({
                    openDropdown: (activateMenuItem && dropdownIdIsString) ? dropdownId : '',
                });
            }
        // If there is no event trigger, user's cursor has left dropdown so we want to close it
        } else if (!isMobile) {
            this.setState({ openDropdown: '' });
        }
    }

    render() {
        return (
            <div id="navbar" className="navbar__wrapper">
                <Navbar
                    brand={<HomeBrand />}
                    brandlink="/"
                    label="main"
                    dropdownClick={this.dropdownClick}
                    openDropdown={this.state.openDropdown}
                    navClasses="navbar-main"
                >
                    <GlobalSections />
                    <SecondarySections isHomePage={this.props.isHomePage} />
                </Navbar>
                {this.state.testWarning ?
                    <div className="test-warning">
                        <div className="container test-warning__content">
                            <div className="test-warning__text">The data displayed on this page is not official and only for testing purposes.</div>
                            <button type="button" className="test-warning__close" onClick={this.handleClickWarning}>
                                <i className="icon icon-times-circle-o" />
                                <span className="sr-only">Close test warning banner</span>
                            </button>
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
};

Navigation.childContextTypes = {
    openDropdown: PropTypes.string, // Identifies dropdown currently dropped down; '' if none
    dropdownClick: PropTypes.func, // Called when a dropdown title gets clicked
};

// Main navigation menus
const GlobalSections = (props, context) => {
    const glossary = require('./glossary/glossary.json');
    const actions = context.listActionsFor('global_sections').map((action) => (
        <NavItem key={action.id} dropdownId={action.id} dropdownTitle={action.title} openDropdown={props.openDropdown} dropdownClick={props.dropdownClick}>
            {action.children ?
                <DropdownMenu label={action.id}>
                    {action.children.map((childAction) => {
                        // Render any separators in the dropdown
                        if (childAction.id.substring(0, 4) === 'sep-') {
                            return <DropdownMenuSep key={childAction.id} />;
                        }
                        const glossaryMatch = glossary.find((def) => def.term.toLowerCase() === childAction.title.toLowerCase());
                        if (glossaryMatch) {
                            return (
                                <div
                                    key={childAction.id}
                                    className={`${childAction.tag ? 'sub-menu' : childAction.url ? '' : 'disabled-menu-item'} ${childAction.url ? 'hoverable' : ''}`}
                                >
                                    <a href={childAction.url || ''}>
                                        {childAction.title}
                                    </a>
                                    <Tooltip
                                        trigger={<i className="icon icon-question-circle" />}
                                        tooltipId={childAction.id}
                                        innerCss={`menu-tooltip ${childAction.tag ? 'sub-menu' : ''}`}
                                        relativeTooltipFlag
                                    >
                                        {glossaryMatch.definition}
                                    </Tooltip>
                                </div>
                            );
                        }
                        // Render any regular linked items in the dropdown
                        return (
                            <a href={childAction.url || ''} key={childAction.id} className={childAction.tag ? 'sub-menu' : childAction.url ? '' : 'disabled-menu-item'} {...childAction.attr}>
                                {childAction.title}
                            </a>
                        );
                    })}
                </DropdownMenu>
            : null}
        </NavItem>
    )).concat(<CartStatus key="cart-control" openDropdown={props.openDropdown} dropdownClick={props.dropdownClick} />);
    return <Nav>{actions}</Nav>;
};

GlobalSections.propTypes = {
    /** ID of the dropdown currently visible */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked */
    dropdownClick: PropTypes.func,
};

GlobalSections.defaultProps = {
    openDropdown: '',
    dropdownClick: null,
};

GlobalSections.contextTypes = {
    listActionsFor: PropTypes.func.isRequired,
};


const SecondarySections = ({ isHomePage, openDropdown, dropdownClick }, context) => {
    const { session } = context;
    const disabled = !session;
    const userActionRender = !(session && session['auth.userid']) ?
        <a href="#!" className="dropdown__toggle" data-trigger="login" disabled={disabled}>Sign in / Create account</a> :
        null;

    return (
        <Nav>
            <NavBarMultiSearch />
            {isHomePage ? null : <ContextActions openDropdown={openDropdown} dropdownClick={dropdownClick} />}
            <UserActions openDropdown={openDropdown} dropdownClick={dropdownClick} />
            <li className="dropdown" id="user-actions-footer">{userActionRender}</li>
        </Nav>);
};

SecondarySections.propTypes = {
    /** True if current page is home page */
    isHomePage: PropTypes.bool,
    /** ID of the dropdown currently visible */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked */
    dropdownClick: PropTypes.func,
};

SecondarySections.contextTypes = {
    session: PropTypes.object, // Login session information
};

SecondarySections.defaultProps = {
    isHomePage: false,
    openDropdown: '',
    dropdownClick: null,
};


// Context actions: mainly for editing the current object
const ContextActions = (props, context) => {
    const actions = context.listActionsFor('context').map((action) => (
        <a href={action.href} key={action.name}>
            <i className="icon icon-pencil" /> {action.title}
        </a>
    ));

    // No action menu
    if (actions.length === 0) {
        return null;
    }

    // Action menu with editing dropdown menu
    if (actions.length > 1) {
        return (
            <NavItem dropdownId="actions" label="Actions" dropdownTitle={<i className="icon icon-gear" />} openDropdown={props.openDropdown} dropdownClick={props.dropdownClick}>
                <DropdownMenu label="actions">
                    {actions}
                </DropdownMenu>
            </NavItem>
        );
    }

    // Action menu without a dropdown menu
    return <NavItem>{actions}</NavItem>;
};

ContextActions.propTypes = {
    /** ID of the dropdown currently visible */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked */
    dropdownClick: PropTypes.func,
};

ContextActions.defaultProps = {
    openDropdown: '',
    dropdownClick: null,
};

ContextActions.contextTypes = {
    listActionsFor: PropTypes.func,
};


const UserActions = (props, context) => {
    const sessionProperties = context.session_properties;
    if (!sessionProperties['auth.userid']) {
        // Logged out, so no user menu at all
        return null;
    }
    const actions = context.listActionsFor('user').map((action) => (
        <a href={action.href || ''} key={action.id} data-bypass={action.bypass} data-trigger={action.trigger}>
            {action.title}
        </a>
    ));
    const { user } = sessionProperties;
    const fullname = (user && user.title) || 'unknown';
    return (
        <NavItem dropdownId="useractions" dropdownTitle={fullname} openDropdown={props.openDropdown} dropdownClick={props.dropdownClick}>
            <DropdownMenu label="useractions">
                {actions}
            </DropdownMenu>
        </NavItem>
    );
};

UserActions.propTypes = {
    /** ID of the dropdown currently visible */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked */
    dropdownClick: PropTypes.func,
};

UserActions.defaultProps = {
    openDropdown: '',
    dropdownClick: null,
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
export const Breadcrumbs = (props) => {
    let accretingQuery = '';
    let accretingTip = '';

    // Get an array of just the crumbs with something in their id
    const crumbs = _.filter(props.crumbs, (crumb) => crumb.id);
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
                    accretingTip += crumb.tip ? (accretingTip.length > 0 ? ' and ' : '') + crumb.tip : '';
                }

                // Append released tag to link and link title if the object is released itself
                const releasedLink = (props.crumbsReleased) ? '&status=released' : '';
                const releasedTag = (props.crumbsReleased) ? 'released ' : '';

                // Render the breadcrumbs
                return (
                    <li key={i}>
                        {(crumb.query || crumb.uri) ?
                            <a
                                href={crumb.uri ? crumb.uri : props.root + accretingQuery + releasedLink}
                                title={crumb.wholeTip ? crumb.wholeTip : `Search for ${accretingTip} in ${releasedTag}${rootTitle}`}
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
    crumbsReleased: PropTypes.bool,
};

Breadcrumbs.defaultProps = {
    root: '',
    crumbsReleased: false,
};
