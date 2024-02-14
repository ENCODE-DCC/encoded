import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { svgIcon } from '../../libs/svg-icons';
import { setCartLockAndSave } from './actions';
import { getReadOnlyState } from './util';


/**
 * Renders a lock icon which, on a user click, initiates the locking of the given cart. That
 * involves setting the `locked` flag in the cart object, though all other processing of this flag
 * happens in the front end.
 */
const CartLockTriggerComponent = ({ cart, inProgress, onLock }) => {
    const readOnlyState = getReadOnlyState(cart);

    // Called when the user clicks the lock/unlock button.
    const handleLockClick = () => {
        onLock(!cart.locked);
    };

    return (
        <div className="cart-tools-extras__button">
            <button
                type="button"
                onClick={handleLockClick}
                className="btn btn-sm btn-warning btn-inline cart-lock-trigger"
                disabled={inProgress || readOnlyState.released}
                aria-label={`${cart.locked ? 'Unlock' : 'Lock'} cart`}
            >
                {svgIcon(cart.locked ? 'lockClosed' : 'lockOpen', { width: 13, marginRight: 4 })}
                {cart.locked ? <span>Unlock</span> : <span>Lock</span>}
            </button>
        </div>
    );
};

CartLockTriggerComponent.propTypes = {
    /** Cart as it exists in the database */
    cart: PropTypes.object.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Redux function called to lock/unlock cart */
    onLock: PropTypes.func.isRequired,
};

const mapDispatchToProps = (dispatch, ownProps) => ({
    onLock: (locked) => dispatch(setCartLockAndSave(locked, ownProps.cart, ownProps.sessionProperties && ownProps.sessionProperties.user, ownProps.fetch)),
});

const CartLockTriggerInternal = connect(null, mapDispatchToProps)(CartLockTriggerComponent);

const CartLockTrigger = (props, reactContext) => (
    <CartLockTriggerInternal {...props} sessionProperties={reactContext.session_properties} fetch={reactContext.fetch} />
);

CartLockTrigger.contextTypes = {
    fetch: PropTypes.func,
    session_properties: PropTypes.object,
};

export default CartLockTrigger;
