/**
 * Components to display the status of the cart in the navigation bar, and to navigate to cart
 * pages.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { DropdownMenu } from '../../libs/bootstrap/dropdown-menu';
import { Nav, NavItem } from '../../libs/bootstrap/navbar';
import { svgIcon } from '../../libs/svg-icons';
import CartShare from './share';


/**
 * Renders the cart icon menu and count in the nav bar.
 */
const CartNavTitle = ({ cart }) => (
    <div className="cart__nav"><div className="cart__nav-icon">{svgIcon('cart')}</div> <div className="cart__nav-count">{cart.length}</div></div>
);

CartNavTitle.propTypes = {
    /** Array of cart contents */
    cart: PropTypes.array.isRequired,
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
        const { cart } = this.props;

        if (this.props.cart.length > 0) {
            const { savedCartObj, openDropdown, dropdownClick, loggedIn } = this.props;

            // Define the menu items for the Cart Status menu.
            const menuItems = [<a key="view" href="/cart-view/">View cart</a>];
            const savedCartAtIds = (savedCartObj && savedCartObj.elements) || [];
            if (loggedIn && savedCartAtIds.length > 0) {
                menuItems.push(<button key="share" onClick={this.shareCartClick}>Share cart</button>);
            }

            return (
                <Nav>
                    <NavItem
                        dropdownId="cart-control"
                        dropdownTitle={<CartNavTitle cart={cart} />}
                        openDropdown={openDropdown}
                        dropdownClick={dropdownClick}
                        label={`Cart containing ${cart.length} ${cart.length > 1 ? 'items' : 'item'}`}
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
    cart: PropTypes.array,
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
    cart: [],
    savedCartObj: null,
    openDropdown: '',
    dropdownClick: null,
    loggedIn: false,
};


const mapStateToProps = (state, ownProps) => ({
    cart: state.cart,
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
