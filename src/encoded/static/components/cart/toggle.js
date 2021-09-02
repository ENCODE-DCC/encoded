/**
 * Renders and handles a button to toggle items in/out of the cart.
 */
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { svgIcon } from '../../libs/svg-icons';
import { addToCartAndSave, removeFromCartAndSave, triggerAlert } from './actions';
import CartLoggedOutWarning, { useLoggedOutWarning } from './loggedout_warning';
import CartMaxElementsWarning from './max_elements_warning';
import { CART_MAX_ELEMENTS, DEFAULT_FILE_VIEW_NAME } from './util';
import { truncateString, uc } from '../globals';


/**
 * Renders and controls the individual cart toggle icons.
 */
const CartToggleComponent = ({
    elements,
    elementAtId,
    savedCartObj,
    displayName,
    css,
    onRemoveFromCartClick,
    onAddToCartClick,
    loggedIn,
    inProgress,
    showMaxElementsWarning,
}) => {
    /** Get hooks for the logged-out warning modal */
    const [loggedOutWarningStates, loggedOutWarningActions] = useLoggedOutWarning(false);

    /**
     * Called when user clicks a toggle button. Depending on whether the element is already in the
     * cart, call the Redux action either to remove from or add to the cart.
     */
    const handleClick = () => {
        if (loggedIn) {
            if (elements.indexOf(elementAtId) === -1) {
                // Toggling an element on (adding to cart) so first make sure we don't exceed the
                // maximum number of elements in the cart with the addition.
                if (savedCartObj.elements.length + 1 > CART_MAX_ELEMENTS) {
                    showMaxElementsWarning();
                } else {
                    onAddToCartClick();
                }
            } else {
                // Toggling an element off (removing from cart).
                onRemoveFromCartClick();
            }
        } else {
            loggedOutWarningActions.setIsWarningVisible(true);
        }
    };

    // Non-logged in users see no toggle.
    const inCart = elements.indexOf(elementAtId) > -1;
    const cartName = (savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.name : '');
    const inCartToolTip = `${inCart ? 'Remove item from cart' : 'Add item to cart'}${cartName ? ` ${uc.ldquo}${cartName}${uc.rdquo}` : ''}`;
    const inProgressToolTip = inProgress ? 'Cart operation in progress' : '';
    const locked = savedCartObj && Object.keys(savedCartObj).length > 0 ? savedCartObj.locked : false;
    const lockedToolTip = locked ? `Cart ${uc.ldquo}${cartName}${uc.rdquo} locked` : '';

    // "name" attribute needed for BDD test targeting.
    return (
        <div className={`cart-toggle${inCart ? ' cart-toggle--in-cart' : ''}${css ? ` ${css}` : ''}`}>
            {displayName && savedCartObj && savedCartObj.name ? <div className="cart-toggle__name">{truncateString(savedCartObj.name, 22)}</div> : null}
            <button
                type="button"
                onClick={handleClick}
                disabled={inProgress || locked}
                title={inProgressToolTip || lockedToolTip || inCartToolTip}
                aria-pressed={inCart}
                aria-label={inProgressToolTip || lockedToolTip || inCartToolTip}
                name={elementAtId}
            >
                {svgIcon('cart', inProgress || locked ? { fill: '#a0a0a0', stroke: '#a0a0a0' } : null)}
            </button>
            {loggedOutWarningStates.isWarningVisible ? <CartLoggedOutWarning closeModalHandler={loggedOutWarningActions.handleCloseWarning} /> : null}
        </div>
    );
};

CartToggleComponent.propTypes = {
    /** Current contents of cart; array of @ids */
    elements: PropTypes.array,
    /** Current cart saved object */
    savedCartObj: PropTypes.object,
    /** @id of element being added to cart */
    elementAtId: PropTypes.string.isRequired,
    /** True to display cart name */
    displayName: PropTypes.bool.isRequired,
    /** CSS to add to toggle */
    css: PropTypes.string.isRequired,
    /** Function to call to add `elementAtId` to cart */
    onAddToCartClick: PropTypes.func.isRequired,
    /** Function to call to remove `elementAtId` from cart  */
    onRemoveFromCartClick: PropTypes.func.isRequired,
    /** True if user is logged in */
    loggedIn: PropTypes.bool,
    /** True if cart operation is in progress */
    inProgress: PropTypes.bool,
    /** Call to show the max elements warning alert */
    showMaxElementsWarning: PropTypes.func.isRequired,
};

CartToggleComponent.defaultProps = {
    elements: [],
    savedCartObj: null,
    loggedIn: false,
    inProgress: false,
};

const mapStateToProps = (state, ownProps) => ({
    elements: state.elements,
    savedCartObj: state.savedCartObj,
    displayName: ownProps.displayName,
    inProgress: state.inProgress,
    elementAtId: ownProps.element['@id'],
    css: ownProps.css,
    loggedIn: ownProps.loggedIn,
});

const mapDispatchToProps = (dispatch, ownProps) => ({
    onAddToCartClick: () => dispatch(addToCartAndSave(ownProps.element['@id'], ownProps.fetch)),
    onRemoveFromCartClick: () => dispatch(removeFromCartAndSave(ownProps.element, ownProps.fileViewTitle, ownProps.fetch)),
    showMaxElementsWarning: () => dispatch(triggerAlert(<CartMaxElementsWarning />)),
});

const CartToggleInternal = connect(mapStateToProps, mapDispatchToProps)(CartToggleComponent);


const CartToggle = (props, reactContext) => (
    <CartToggleInternal
        element={props.element}
        displayName={props.displayName}
        fileViewTitle={DEFAULT_FILE_VIEW_NAME}
        css={props.css}
        loggedIn={!!(reactContext.session && reactContext.session['auth.userid'])}
        fetch={reactContext.fetch}
    />
);

CartToggle.propTypes = {
    /** Object being added */
    element: PropTypes.object.isRequired,
    /** True to show cart name next to toggle */
    displayName: PropTypes.bool,
    /** CSS to add to toggle */
    css: PropTypes.string,
};

CartToggle.defaultProps = {
    displayName: false,
    css: '',
};

CartToggle.contextTypes = {
    session: PropTypes.object,
    fetch: PropTypes.func,
};

export default CartToggle;
