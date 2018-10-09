import React from 'react';
import PropTypes from 'prop-types';


// This module handles menu bars, and combined with the <DropdownMenu> component, handles dropdown
// menus within menu bars. To use it, you must first include the `Navbars` mixin in the component
// that renders the menu bars.
//
// Use these components like this:
//
// render: function () {
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
//              </Nav>
//              <Nav>
//                  ...
//              </Nav>
//          </Navbar>
//     );
// }


// Controls an entire navigation menu with one or more navigation areas defined by <Nav>
// components. Handles the toggling of the mobile menu expansion.
export class Navbar extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = {
            expanded: false, // True if mobile version of menu is expanded
        };

        // Bind this to non-React methods.
        this.collapseClick = this.collapseClick.bind(this);
    }

    collapseClick() {
        // Click on the Navbar mobile "collapse" button
        this.setState(prevState => ({ expanded: !prevState.expanded }));
    }

    render() {
        const { brand, brandlink, label, navClasses, openDropdown, dropdownClick } = this.props;

        // Add openDropdown and dropdownClick props to the child components.
        let children = [];
        if (this.props.children && this.props.children.length) {
            children = React.Children.map(this.props.children, child => (
                child ? React.cloneElement(child, { openDropdown, dropdownClick }) : null
            ));
        }

        return (
            <nav className={`navbar ${navClasses || 'navbar-default'}`}>
                <div className="navbar-header">
                    <button data-trigger className="navbar-toggle collapsed" data-toggle="collapse" data-target={label} aria-expanded={this.state.expanded} onClick={this.collapseClick}>
                        <span className="sr-only">Toggle navigation</span>
                        <span className="icon-bar" />
                        <span className="icon-bar" />
                        <span className="icon-bar" />
                    </button>
                    {brand ?
                        <a className="navbar-brand" href={brandlink}>{brand}</a>
                    : null}
                </div>

                <div className={`collapse navbar-collapse${this.state.expanded ? ' in' : ''}`} id={label}>
                    {children}
                </div>
            </nav>
        );
    }
}

Navbar.propTypes = {
    brand: PropTypes.oneOfType([ // String or component to display for the brand with class `navbar-brand`
        PropTypes.string,
        PropTypes.object,
    ]),
    brandlink: PropTypes.string, // href for clicking brand
    label: PropTypes.string.isRequired, // id for nav; unique on page
    navClasses: PropTypes.string, // CSS classes for <nav> in addition to "navbar"; default to "navbar-default"
    openDropdown: PropTypes.string.isRequired, // ID of the dropdown currently visible
    dropdownClick: PropTypes.func.isRequired, // Function to call when dropdown clicked
    children: PropTypes.node, // Child menus to display in the menu bar
};

Navbar.defaultProps = {
    brand: null,
    brandlink: '',
    navClasses: '',
    children: null,
};


// Controls one navigation area within a <Navbar>
export const Nav = props => (
    <ul className={`nav navbar-nav${props.right ? ' navbar-right' : ''}`}>
        {props.children}
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
        <li className={dropdownId ? `dropdown${dropdownOpen ? ' open' : ''}` : ''}>
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
    dropdownId: PropTypes.string, // If this item has a dropdown, this ID helps manage it; must be unique
    dropdownTitle: PropTypes.oneOfType([ // If this item has a dropdown, this is the title
        PropTypes.string,
        PropTypes.object,
    ]),
    openDropdown: PropTypes.string,
    dropdownClick: PropTypes.func,
    label: PropTypes.string, // Navigation button aria label text
    buttonCss: PropTypes.string, // CSS classes to add to navigation button
    children: PropTypes.node, // Child components within one menu item, likely just text
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
                className={`dropdown-toggle${css ? ` ${css}` : ''}`}
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded={dropdownOpen}
                aria-label={label}
                onClick={this.clickHandler}
            >
                {dropdownTitle}
            </button>
        );
    }
}

NavItemButton.propTypes = {
    clickHandler: PropTypes.func, // Parent function to react to clicks in this dropdown menu title
    dropdownOpen: PropTypes.bool, // True if the dropdown menu for this item is visible
    dropdownId: PropTypes.string, // ID of the dropdown that was clicked
    dropdownTitle: PropTypes.oneOfType([ // Title to display within the actutor part of the dropdown
        PropTypes.string,
        PropTypes.object,
    ]),
    label: PropTypes.string, // aria-label text
    css: PropTypes.string, // CSS classes to add to button
};

NavItemButton.defaultProps = {
    clickHandler: null,
    dropdownOpen: false,
    dropdownId: '',
    dropdownTitle: null,
    label: '',
    css: '',
};
