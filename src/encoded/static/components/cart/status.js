/**
 * Components to display the status of the cart in the navigation bar, and to navigate to cart
 * pages.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { DropdownMenu, DropdownMenuSep } from '../../libs/bootstrap/dropdown-menu';
import { Nav, NavItem } from '../../libs/bootstrap/navbar';
import { svgIcon } from '../../libs/svg-icons';
import { truncateString } from '../globals';
import CartShare from './share';


/**
 * Renders the cart icon menu and count in the nav bar.
 */
const CartNavTitle = ({ elements }) => (
    <div className="cart__nav"><div className={`cart__nav-icon${elements.length === 0 ? ' cart__nav-icon--empty' : ''}`}>{svgIcon('cart')}</div> {elements.length > 0 ? <div className="cart__nav-count">{elements.length}</div> : null}</div>
);

CartNavTitle.propTypes = {
    /** Array of cart contents */
    elements: PropTypes.array.isRequired,
};


/**
 * Navigation bar item for the cart menu, including a simple link to the cart page, as well as a
 * button that brings up the Share Cart modal.
 */
class CartStatusComponent extends React.Component {
    constructor() {
        super();
        this.state = {
            /** True if Share Cart modal is visible */
            shareModalOpen: false,
        };
        this.shareCartClick = this.shareCartClick.bind(this);
        this.closeShareCart = this.closeShareCart.bind(this);
    }

    /**
     * Called when the Share Cart menu item is clicked.
     */
    shareCartClick() {
        this.setState({ shareModalOpen: true });
    }

    /**
     * Called when the Share Cart modal close buttons are clicked.
     */
    closeShareCart() {
        this.setState({ shareModalOpen: false });
    }

    render() {
        const { elements, savedCartObj, openDropdown, dropdownClick, loggedIn } = this.props;

        if (loggedIn || elements.length > 0) {
            // Define the menu items for the Cart Status menu.
            const cartName = truncateString(savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '', 30);
            const menuItems = [];
            const viewCartItem = <a key="view" href="/cart-view/">View cart{cartName ? <span>: {cartName}</span> : null}</a>;
            if (loggedIn) {
                if (elements.length > 0) {
                    menuItems.push(
                        viewCartItem,
                        <button key="share" onClick={this.shareCartClick}>Share cart{cartName ? <span>: {cartName}</span> : null}</button>,
                        <DropdownMenuSep key="sep" />
                    );
                }
                menuItems.push(<a key="manage" href="/cart-manager/">Cart manager</a>);
            } else {
                menuItems.push(viewCartItem);
            }

            return (
                <Nav>
                    <NavItem
                        dropdownId="cart-control"
                        dropdownTitle={<CartNavTitle elements={elements} />}
                        openDropdown={openDropdown}
                        dropdownClick={dropdownClick}
                        label={`Cart containing ${elements.length} ${elements.length > 1 ? 'items' : 'item'}`}
                        buttonCss="cart__nav-button"
                    >
                        <DropdownMenu label="cart-control">
                            {menuItems}
                        </DropdownMenu>
                    </NavItem>
                    {this.state.shareModalOpen ? <CartShare userCart={savedCartObj} closeShareCart={this.closeShareCart} /> : null}
                </Nav>
            );
        }
        return null;
    }
}

CartStatusComponent.propTypes = {
    /** Cart contents as array of @ids */
    elements: PropTypes.array,
    /** Cached saved cart object */
    savedCartObj: PropTypes.object,
    /** ID of nav dropdown currently visible */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked */
    dropdownClick: PropTypes.func,
    /** True if user has logged in */
    loggedIn: PropTypes.bool,
};

CartStatusComponent.defaultProps = {
    elements: [],
    savedCartObj: null,
    openDropdown: '',
    dropdownClick: null,
    loggedIn: false,
};


const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj || null,
    openDropdown: ownProps.openDropdown,
    dropdownClick: ownProps.dropdownClick,
    loggedIn: !!(ownProps.session && ownProps.session['auth.userid']),
});

const CartStatusInternal = connect(mapStateToProps)(CartStatusComponent);


/**
 * Public Redux component to display the cart menu in the navigation bar. This is a <Navbar> child
 * so it gets its properties automatically imported from <Navbar>.
 */
const CartStatus = ({ openDropdown, dropdownClick }, reactContext) => (
    <CartStatusInternal
        openDropdown={openDropdown}
        dropdownClick={dropdownClick}
        session={reactContext.session}
    />
);

CartStatus.propTypes = {
    /** ID of nav dropdown currently visible; copied from <Navbar> props */
    openDropdown: PropTypes.string,
    /** Function to call when dropdown clicked; copied from <Navbar> props */
    /** Note: Required, but props from React.cloneElement fail isRequired validation */
    dropdownClick: PropTypes.func,
};

CartStatus.defaultProps = {
    openDropdown: '',
    dropdownClick: null,
};

CartStatus.contextTypes = {
    session: PropTypes.object,
};

export default CartStatus;
