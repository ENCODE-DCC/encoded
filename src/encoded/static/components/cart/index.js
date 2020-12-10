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
 * "active" carts hold the current cart contents that users add new elements to. "shared" carts are
 * contents of a cart object from the database and can be shared with others.
 */
import { createStore, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import _ from 'underscore';
import { contentViews } from '../globals';
import {
    ADD_TO_CART,
    ADD_MULTIPLE_TO_CART,
    REMOVE_FROM_CART,
    REMOVE_MULTIPLE_FROM_CART,
    REPLACE_CART,
    CACHE_SAVED_CART,
    CART_OPERATION_IN_PROGRESS,
    SET_CURRENT,
    SET_NAME,
    SET_IDENTIFIER,
    SET_LOCKED,
    SET_STATUS,
    NO_ACTION,
} from './actions';
import cartAddElements from './add_elements';
import { CartAddAllSearch, CartAddAllElements } from './add_multiple';
import cartCacheSaved from './cache_saved';
import CartBatchDownload from './batch_download';
import Cart from './cart';
import CartClear from './clear';
import cartSetOperationInProgress from './in_progress';
import CartMergeShared from './merge_shared';
import cartRemoveElements from './remove_elements';
import cartSave, { cartCreateAutosave, cartRetrieve } from './database';
import CartManager from './manager';
import cartSetCurrent from './set_current';
import CartSearchControls from './search_controls';
import { cartGetSettings, cartSetSettingsCurrent } from './settings';
import CartShare from './share';
import CartStatus from './status';
import switchCart from './switch';
import CartToggle from './toggle';
import { mergeCarts, cartGetAllowedTypes, cartGetAllowedObjectPathTypes } from './util';


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
            if (state.elements.indexOf(action.elementAtId) === -1) {
                return Object.assign({}, state, {
                    elements: state.elements.concat([action.elementAtId]),
                });
            }
            return state;
        case ADD_MULTIPLE_TO_CART: {
            const elements = mergeCarts(state.elements, action.elementAtIds);
            return Object.assign({}, state, {
                elements,
            });
        }
        case REMOVE_FROM_CART: {
            const doomedIndex = state.elements.indexOf(action.elementAtId);
            if (doomedIndex !== -1) {
                return Object.assign({}, state, {
                    elements: state.elements
                        .slice(0, doomedIndex)
                        .concat(state.elements.slice(doomedIndex + 1)),
                });
            }
            return state;
        }
        case REMOVE_MULTIPLE_FROM_CART:
            return Object.assign({}, state, {
                elements: _.difference(state.elements, action.elementAtIds),
            });
        case REPLACE_CART:
            return Object.assign({}, state, {
                elements: action.elementAtIds,
            });
        case CACHE_SAVED_CART:
            return Object.assign({}, state, {
                savedCartObj: action.savedCartObj,
            });
        case CART_OPERATION_IN_PROGRESS:
            return Object.assign({}, state, { inProgress: action.inProgress });
        case SET_NAME:
            return Object.assign({}, state, { name: action.name });
        case SET_IDENTIFIER:
            return Object.assign({}, state, { identifier: action.identifier });
        case SET_LOCKED:
            return Object.assign({}, state, { locked: action.locked });
        case SET_CURRENT:
            return Object.assign({}, state, { current: action.current });
        case SET_STATUS:
            return Object.assign({}, state, { status: action.status });
        default:
            return state;
        }
    }
    return null;
};


/**
 * Merge elements into a cart without duplication.
 * @param {object} cart Cart object to merge elements into
 * @param {array} elements Array of @ids to merge into `cart`
 * @return {object} New cart object with merged elements
 */
const cartMergeElements = (cart, elements) => {
    const mergedElements = mergeCarts(cart.elements, elements);
    return Object.assign({}, cart, { elements: mergedElements });
};


/**
 * Switch the current cart to a saved cart given its @id. Do not rely on the return value.
 * @param {string} cartAtId @id of the cart to switch the current one to
 * @param {func} fetch System fetch function
 * @param {func} dispatch Redux dispatch function
 */
const cartSwitch = (cartAtId, fetch, dispatch) => (
    dispatch(switchCart(cartAtId, fetch))
);


/**
 * Create a Redux store for the cart; normally done on page load.
 * @return {object} Redux store object
 */
const initializeCart = () => {
    const initialCart = {
        /** Active cart contents as array of @ids */
        elements: [],
        /** Human-readable name for the cart */
        name: 'Untitled',
        /** Cart identifier used in URI */
        identifier: 'untitled',
        /** Initial unlocked cart */
        locked: false,
        /** @id of current cart */
        current: '',
        /** Cache of saved cart */
        savedCartObj: {},
        /** Indicates cart operations currently in progress */
        inProgress: false,
    };
    return createStore(cartModule, initialCart, applyMiddleware(thunk));
};


/**
 * Create the cart store at page load.
 */
const cartStore = initializeCart();


// Include any symbols needed outside the "cart" directory.
export {
    CartAddAllSearch,
    CartAddAllElements,
    CartBatchDownload,
    cartCacheSaved,
    CartClear,
    cartCreateAutosave,
    cartGetSettings,
    cartSetSettingsCurrent,
    CartMergeShared,
    cartMergeElements,
    cartRemoveElements,
    cartRetrieve,
    cartSetOperationInProgress,
    CartSearchControls,
    cartSetCurrent,
    CartStatus,
    cartStore as default,
    CartToggle,
    cartAddElements,
    CartShare,
    cartSave,
    cartSwitch,
    // Export the following for Jest tests
    cartModule,
    CartManager,
    cartGetAllowedTypes,
    cartGetAllowedObjectPathTypes,
};


contentViews.register(Cart, 'cart-view'); // /cart-view/ URI
contentViews.register(Cart, 'Cart'); // /carts/<uuid> URI
contentViews.register(CartManager, 'cart-manager'); // /cart-manager/ URI
