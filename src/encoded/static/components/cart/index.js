/**
 * This file lets other files import this directory to get the cart Redux reducer function and any
 * cart-related rendering components.
 *
 * You'll see references to terms used for various kinds of carts:
 *
 * active - The in-memory representation of the cart held in a Redux store
 * shared - The cart in a user's `carts` object referenced by "/carts/<uuid>"
 * saved - The cart contents in a user's `carts` object
 *
 * "active" carts hold saved (if logged in) and unsaved (if logged out) elements. "shared" carts
 * hold saved elements. Users who aren't logged in can only have an "active" cart. "shared" carts,
 * when displayed with the cart's uuid, can be shared with others.
 */
import { createStore, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import _ from 'underscore';
import {
    ADD_TO_CART,
    ADD_MULTIPLE_TO_CART,
    REMOVE_FROM_CART,
    REMOVE_MULTIPLE_FROM_CART,
    CACHE_SAVED_CART,
    CART_OPERATION_IN_PROGRESS,
    NO_ACTION,
} from './actions';
import cartAddElements from './add_elements';
import CartAddAll from './add_multiple';
import cartCacheSaved from './cache_saved';
import CartBatchDownload from './batch_download';
import CartClear from './clear';
import cartSetOperationInProgress from './in_progress';
import CartMergeShared from './merge_shared';
import cartRemoveElements from './remove_elements';
import cartSave from './save';
import CartSearchControls from './search_controls';
import CartShare from './share';
import CartStatus from './status';
import CartToggle from './toggle';
import { mergeCarts } from './util';


/**
 * Redux reducer function for the cart module. Redux requires this be a pure function -- the
 * incoming `state` must not be mutated for the resulting state object.
 * @param {object} state - Redux store state
 * @param {object} action - Action to perform on the cart store
 * @return {object} New cart state object, or null if parameters make no sense
 */
const cartModule = (state, action = { type: NO_ACTION }) => {
    if (state) {
        switch (action.type) {
        case ADD_TO_CART:
            if (state.cart.indexOf(action.elementAtId) === -1) {
                return Object.assign({}, state, {
                    cart: state.cart.concat([action.elementAtId]),
                });
            }
            return state;
        case ADD_MULTIPLE_TO_CART: {
            const elements = mergeCarts(state.cart, action.elementAtIds);
            return Object.assign({}, state, {
                cart: elements,
            });
        }
        case REMOVE_FROM_CART: {
            const doomedIndex = state.cart.indexOf(action.elementAtId);
            if (doomedIndex !== -1) {
                return Object.assign({}, state, {
                    cart: state.cart
                        .slice(0, doomedIndex)
                        .concat(state.cart.slice(doomedIndex + 1)),
                });
            }
            return state;
        }
        case REMOVE_MULTIPLE_FROM_CART:
            return Object.assign({}, state, {
                cart: _.difference(state.cart, action.elementAtIds),
            });
        case CACHE_SAVED_CART:
            return Object.assign({}, state, {
                savedCartObj: action.savedCartObj,
            });
        case CART_OPERATION_IN_PROGRESS:
            return Object.assign({}, state, { inProgress: action.inProgress });
        default:
            return state;
        }
    }
    return null;
};


/**
 * Create a Redux store for the cart; normally done on page load.
 * @return {object} Redux store object
 */
const initializeCart = () => {
    const initialCart = {
        cart: [], // Active cart contents as array of @ids
        name: 'Untitled',
        savedCartObj: {}, // Cache of saved cart
        inProgress: false, // No long operations currently in progress
    };
    return createStore(cartModule, initialCart, applyMiddleware(thunk));
};


// Include any symbols needed outside the "cart" directory.
export {
    CartAddAll,
    CartBatchDownload,
    cartCacheSaved,
    CartClear,
    CartMergeShared,
    cartRemoveElements,
    cartSetOperationInProgress,
    CartSearchControls,
    CartStatus,
    CartToggle,
    cartAddElements,
    CartShare,
    cartSave,
    cartModule, // Exported for Jest tests
    initializeCart as default,
};
