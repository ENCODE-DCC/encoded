/**
 * Components to display the status of the cart in the navigation bar, and to navigate to cart
 * pages.
 */
import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { DropdownMenu, DropdownMenuSep } from '../../libs/ui/dropdown-menu';
import { NavItem } from '../../libs/ui/navbar';
import { svgIcon } from '../../libs/svg-icons';
import { truncateString } from '../globals';
import Status from '../status';
import { CartClearModal } from './clear';
import CartShare from './share';


/**
 * Renders the cart icon menu and count or in-progress spinner in the nav bar.
 */
const CartNavTitle = ({ elements, inProgress, locked }) => {
    let status;
    let iconClass = '';

    if (inProgress) {
        status = svgIcon('spinner');
        iconClass = 'cart__nav-spinner';
    } else if (elements.length > 0) {
        status = elements.length;
        iconClass = 'cart__nav-count';
    }
    return (
        <div className="cart__nav">
            <div className={`cart__nav-icon${status ? '' : ' cart__nav-icon--empty'}`}>
                {svgIcon('cart', { fill: locked ? '#e59545' : '#fff' })}
            </div>
            {status ? <div className={iconClass}>{status}</div> : null}
        </div>
    );
};

CartNavTitle.propTypes = {
    /** Array of cart contents */
    elements: PropTypes.array.isRequired,
    /** True if global cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** True if cart is locked */
    locked: PropTypes.bool.isRequired,
};


/**
 * Navigation bar item for the cart menu.
 */
const CartStatusComponent = ({ elements, savedCartObj, inProgress, openDropdown, dropdownClick, loggedIn }) => {
    /** True if the modal to share a cart is open */
    const [shareModalOpen, setSharedModalOpen] = React.useState(false);
    /** True if the modal to clear a cart is open */
    const [clearModalOpen, setClearModalOpen] = React.useState(false);

    /**
     * Called when the Share Cart menu item is clicked.
     */
    const shareCartClick = () => {
        setSharedModalOpen(true);
    };

    /**
     * Called when the Share Cart modal close buttons are clicked.
     */
    const closeShareCart = () => {
        setSharedModalOpen(false);
    };

    /**
     * Called when the Clear Cart menu item is clicked.
     */
    const clearCartClick = () => {
        setClearModalOpen(true);
    };

    /**
     * Called when the Clear Cart modal close buttons are clicked.
     */
    const closeClearCart = () => {
        setClearModalOpen(false);
    };

    // Define the menu items for the Cart Status menu.
    const viewCartItem = <a key="view" href="/cart-view/">View cart</a>;
    const clearCartItem = !savedCartObj.locked && <button type="button" key="clear" onClick={clearCartClick}>Clear cart</button>;
    const menuItems = [];
    if (loggedIn) {
        // Build the disabled cart name and lock status.
        const cartName = (savedCartObj && savedCartObj.name) && truncateString(savedCartObj.name, 22);
        const lockIcon = cartName && <div className="cart-nav-lock">{svgIcon(savedCartObj.locked ? 'lockClosed' : 'lockOpen')}</div>;
        const statusIcon = savedCartObj && savedCartObj.status && <Status item={savedCartObj} css="cart-menu-status" badgeSize="small" noLabel inline />;
        menuItems.push(
            <span key="name" className="disabled-menu-item">
                {statusIcon}{`Current: ${cartName}`}{lockIcon}
            </span>,
            <DropdownMenuSep key="sep-1" />
        );

        // Menu items for carts containing items.
        if (elements.length > 0) {
            menuItems.push(
                viewCartItem,
                <button type="button" key="share" onClick={shareCartClick}>Share cart</button>,
                clearCartItem,
                <DropdownMenuSep key="sep-2" />
            );
        }

        // Menu item for the cart manager and cart list.
        menuItems.push(<a key="manager" href="/cart-manager/">Cart manager</a>);
    } else {
        // Menu item to offer to log in
        menuItems.push(
            <button key="signin" type="button" data-trigger="login">
                Sign in / Create account
            </button>
        );
    }

    // Menu item for cart listing always visible.
    menuItems.push(<a key="search" href="/search/?type=Cart&status=listed&status=released">Listed carts</a>);

    return (
        <NavItem
            dropdownId="cart-control"
            dropdownTitle={<CartNavTitle elements={elements} locked={savedCartObj.locked || false} inProgress={inProgress} />}
            openDropdown={openDropdown}
            dropdownClick={dropdownClick}
            label={`${savedCartObj.locked ? 'locked' : ''} cart containing ${elements.length} ${elements.length > 1 ? 'items' : 'item'}`}
            buttonCss="cart__nav-button"
        >
            <DropdownMenu label="cart-control">
                {menuItems}
            </DropdownMenu>
            {shareModalOpen ? <CartShare userCart={savedCartObj} closeShareCart={closeShareCart} /> : null}
            {clearModalOpen ? <CartClearModal closeClickHandler={closeClearCart} /> : null}
        </NavItem>
    );
};

CartStatusComponent.propTypes = {
    /** Cart contents as array of @ids */
    elements: PropTypes.array,
    /** Cached saved cart object */
    savedCartObj: PropTypes.object,
    /** True if global cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
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
    inProgress: state.inProgress,
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
