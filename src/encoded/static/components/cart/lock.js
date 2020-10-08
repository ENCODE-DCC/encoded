import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { svgIcon } from '../../libs/svg-icons';
import { setCartLockAndSave } from './actions';


/**
 * Renders a lock icon which, on a user click, initiates the locking of the given cart. That
 * involves setting the `locked` flag in the cart object, though all other processing of this flag
 * happens in the front end.
 */
const CartLockTriggerComponent = ({ savedCartObj, inProgress, onLock }) => {
    // Called when the user clicks the lock/unlock button.
    const handleLockClick = () => {
        onLock(!savedCartObj.locked);
    };

    // Determine the tooltip text.
    let disabledTooltip = '';
    if (savedCartObj.status === 'deleted') {
        disabledTooltip = 'Cannot lock a deleted cart';
    } else if (savedCartObj.status === 'disabled') {
        disabledTooltip = 'Cannot share the auto-save cart';
    } else if (inProgress) {
        disabledTooltip = 'Cart operation in progress';
    }

    return (
        <div className="cart-manager-table__tooltip-group cart-tools-extras__button">
            {disabledTooltip ?
                <div
                    className="cart-manager-table__button-overlay"
                    title={disabledTooltip}
                />
            : null}
            <button
                onClick={handleLockClick}
                className="btn btn-sm btn-warning btn-inline cart-lock-trigger"
                disabled={inProgress || savedCartObj.status === 'deleted' || savedCartObj.status === 'disabled'}
                aria-label={`${savedCartObj.locked ? 'Unlock' : 'Lock'} cart`}
            >
                {svgIcon(savedCartObj.locked ? 'lockClosed' : 'lockOpen', { width: 13, marginRight: 4 })}
                {savedCartObj.locked ? <span>Unlock</span> : <span>Lock</span>}
            </button>
        </div>
    );
};

CartLockTriggerComponent.propTypes = {
    /** Cart as it exists in the database */
    savedCartObj: PropTypes.object.isRequired,
    /** True if cart operation in progress */
    inProgress: PropTypes.bool.isRequired,
    /** Redux function called to lock/unlock cart */
    onLock: PropTypes.func.isRequired,
};

const mapDispatchToProps = (dispatch, ownProps) => ({
    onLock: locked => dispatch(setCartLockAndSave(locked, ownProps.savedCartObj, ownProps.sessionProperties && ownProps.sessionProperties.user, ownProps.fetch)),
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
