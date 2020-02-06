import React from 'react';
import PropTypes from 'prop-types';


// This module handles menu bars, and combined with the <DropdownMenu> component, handles dropdown
// menus within menu bars. To use it, you must first include the `Navbars` mixin in the component
// that renders the menu bars.
//
// Use these components like this:
//
// render() {
//     return (
//         <Navbar>
//             <Nav>
//                 <NavItem>
//                     <a href="/">Standalone Item</a>
//                 </NavItem>
//                 <NavItem title="Dropdown Menu">
//                     <DropdownMenu>
//                         <a href="/">Dropdown Item</a>
//                     </DropdownMenu>
//                 </NavItem>
//             </Nav>
//             <Nav>
//                 ...
//             </Nav>
//         </Navbar>
//     );
// }


/**
 * Displays and reacts to clicks in the hamburger menu button
 */
const HamburgerTrigger = ({ expanded, navigationId, clickHandler }) => (
    <button className={`navbar__trigger${expanded ? '' : ' collapsed'}`} aria-label="Navigation trigger" aria-controls={navigationId} aria-expanded={expanded} onClick={clickHandler}>
        <svg focusable="false" width="29" height="29" viewBox="0 0 29 29">
            <path d="M27.92,5H1.08C0.48,5,0,4.52,0,3.92V1.08C0,0.48,0.48,0,1.08,0h26.85C28.52,0,29,0.48,29,1.08v2.85 C29,4.52,28.52,5,27.92,5z" />
            <path d="M27.92,17H1.08C0.48,17,0,16.52,0,15.92v-2.85C0,12.48,0.48,12,1.08,12h26.85c0.59,0,1.08,0.48,1.08,1.08v2.85 C29,16.52,28.52,17,27.92,17z" />
            <path d="M27.92,29H1.08C0.48,29,0,28.52,0,27.92v-2.85C0,24.48,0.48,24,1.08,24h26.85c0.59,0,1.08,0.48,1.08,1.08v2.85 C29,28.52,28.52,29,27.92,29z" />
        </svg>
    </button>
);

HamburgerTrigger.propTypes = {
    /** True if mobile menu is expanded */
    expanded: PropTypes.bool,
    /** Element ID of collapsable mobile menu this trigger controls */
    navigationId: PropTypes.string,
    /** Callback for clicks in the trigger button */
    clickHandler: PropTypes.func.isRequired,
};

HamburgerTrigger.defaultProps = {
    expanded: false,
    navigationId: '',
};


/**
 * Controls an entire navigation menu with one or more navigation areas defined by <Nav>
 * components. Handles the toggling of the mobile menu expansion, and provides a property and
 * function for handling clicks in dropdowns. <Navbar> passes an `openDropdown` and `dropdownClick`
 * prop to all direct child components, so any components intervening between <Navbar> and
 * <NavItem> must pass along the `openDropdown` and `dropdownClick` props to their descendants.
 */
export class Navbar extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = {
            /** True if mobile version of menu is expanded */
            expanded: false,
        };

        // Bind this to non-React methods.
        this.collapseClick = this.collapseClick.bind(this);
    }

    /**
      * Click on the Navbar mobile "collapse" button.
      */
    collapseClick() {
        this.setState(prevState => ({ expanded: !prevState.expanded }));
    }

    render() {
        const { brand, brandlink, label, dropdownClick, openDropdown } = this.props;

        // Add openDropdown and dropdownClick props to the child components.
        let children = [];
        if (this.props.children && this.props.children.length > 0) {
            children = React.Children.map(this.props.children, child => (
                child ? React.cloneElement(child, { openDropdown, dropdownClick }) : null
            ));
        }

        // Handle the brand link or component.
        let brandComponent = null;
        if (brand) {
            brandComponent = typeof brand === 'string' ? <a href={brandlink}>{brand}</a> : brand;
        }

        return (
            <nav className="navbar">
                <div className="navbar__container">
                    <div className="navbar__header">
                        {brand ? <div className="navbar__brand">{brandComponent}</div> : null}
                        <HamburgerTrigger expanded={this.state.expanded} navigationId={label} clickHandler={this.collapseClick} />
                    </div>

                    <div className={`navbar__content${this.state.expanded ? '' : ' collapsed'}`} id={label}>
                        {children}
                    </div>
                </div>
            </nav>
        );
    }
}

Navbar.propTypes = {
    /** Display for the optional brand */
    brand: PropTypes.oneOfType([
        PropTypes.string, // Brand is text with optional link
        PropTypes.object, // Brand is a React component
    ]),
    /** href used when clicking string brand */
    brandlink: PropTypes.string,
    /** id for div containing Nav items; unique on page */
    label: PropTypes.string.isRequired,
    /** Callback when the user clicks a menu item */
    dropdownClick: PropTypes.func.isRequired,
    /** ID of menu currently dropped down, or '' */
    openDropdown: PropTypes.string.isRequired,
    /** Child <Nav> items to display in the navigation bar */
    children: PropTypes.node,
};

Navbar.defaultProps = {
    brand: null,
    brandlink: '',
    children: null,
};


/**
 * Wraps around one navigation area, mostly for CSS styling when dividing up multiple navigation
 * areas within a <NavBar>.
 */
export const Nav = ({ right, children }) => (
    <ul className={`navbar__nav${right ? ' navbar__nav--right' : ''}`}>
        {children}
    </ul>
);

Nav.propTypes = {
    right: PropTypes.bool, // True if right-justified navigation area
    children: PropTypes.node, // Menu items to draw within the menu
};

Nav.defaultProps = {
    right: false,
    children: null,
};


// Controls one top-level item within a <Nav>. It can be a stand-alone item or a dropdown menu
export const NavItem = (props) => {
    const { dropdownId, dropdownTitle, label, buttonCss } = props;
    const dropdownOpen = dropdownId && (props.openDropdown === dropdownId);

    return (
        <li
            className={dropdownId ? `dropdown${dropdownOpen ? ' open' : ''}` : null}
            onMouseLeave={props.dropdownClick}
        >
            {dropdownTitle ?
                <NavItemButton
                    clickHandler={props.dropdownClick}
                    dropdownOpen={dropdownOpen}
                    dropdownTitle={dropdownTitle}
                    dropdownId={dropdownId}
                    label={label}
                    css={buttonCss}
                />
            : null}
            {props.children}
        </li>
    );
};

NavItem.propTypes = {
    /** If this item has a dropdown, this ID helps manage it; must be unique */
    dropdownId: PropTypes.string,
    /** If this item has a dropdown, this renders the title */
    dropdownTitle: PropTypes.oneOfType([
        PropTypes.string, // Title passed directly
        PropTypes.object, // Title rendered by a component
    ]),
    /** True if this dropdown has been dropped down/is visible */
    openDropdown: PropTypes.string,
    /** Function to call to indicate the dropdown title has been clicked */
    dropdownClick: PropTypes.func,
    /** Navigation button aria label text */
    label: PropTypes.string,
    /** CSS classes to add to navigation button */
    buttonCss: PropTypes.string,
    /** Child components within one menu item, likely just text */
    children: PropTypes.node,
};

NavItem.defaultProps = {
    dropdownId: '',
    dropdownTitle: null,
    openDropdown: '',
    dropdownClick: null,
    label: '',
    buttonCss: '',
    children: null,
};


class NavItemButton extends React.Component {
    constructor() {
        super();

        // Bind this to non-React components.
        this.clickHandler = this.clickHandler.bind(this);
    }

    clickHandler(e) {
        if (this.props.clickHandler) {
            this.props.clickHandler(this.props.dropdownId, e);
        }
    }

    render() {
        const { dropdownOpen, dropdownTitle, dropdownId, label, css } = this.props;
        return (
            <button
                id={dropdownId}
                className={`dropdown__toggle${dropdownOpen ? ' dropdown__toggle--open' : ''}${css ? ` ${css}` : ''}`}
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded={dropdownOpen}
                aria-label={label}
                onClick={this.clickHandler}
                onMouseEnter={this.clickHandler}
            >
                {dropdownTitle}
            </button>
        );
    }
}

NavItemButton.propTypes = {
    /** Parent function to react to clicks in this dropdown menu title */
    clickHandler: PropTypes.func,
    /** True if the dropdown menu for this item is visible */
    dropdownOpen: PropTypes.bool,
    /** ID of the dropdown that was clicked */
    dropdownId: PropTypes.string,
    /** Title to display within the actuator part of the dropdown */
    dropdownTitle: PropTypes.oneOfType([
        PropTypes.string,
        PropTypes.object,
    ]),
    /** aria-label text */
    label: PropTypes.string,
    /** CSS classes to add to button */
    css: PropTypes.string,
};

NavItemButton.defaultProps = {
    clickHandler: null,
    dropdownOpen: false,
    dropdownId: '',
    dropdownTitle: null,
    label: '',
    css: '',
};
