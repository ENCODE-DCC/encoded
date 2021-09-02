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
    CLEAR_CART,
    ADD_FILE_VIEW,
    REMOVE_FILE_VIEW,
    ADD_TO_FILE_VIEW,
    REMOVE_FROM_FILE_VIEW,
    REPLACE_FILE_VIEWS,
    REPLACE_CART,
    CACHE_SAVED_CART,
    CART_OPERATION_IN_PROGRESS,
    DISPLAY_ALERT,
    SET_CURRENT,
    SET_NAME,
    SET_IDENTIFIER,
    SET_LOCKED,
    SET_STATUS,
    NO_ACTION,
} from './actions';
import cartAddElements from './add_elements';
import CartAlert from './cart_alert';
import { CartAddAllSearch, CartAddAllElements } from './add_multiple';
import cartCacheSaved from './cache_saved';
import CartBatchDownload from './batch_download';
import Cart from './cart';
import CartClear from './clear';
import CartFileViewToggleComponent from './file_view';
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
import {
    cartGetAllowedObjectPathTypes,
    cartGetAllowedTypes,
    getCartSearchTypes,
    getIsCartSearch,
    mergeCarts,
    CART_MAX_ELEMENTS,
} from './util';


/**
 * Generates a new fileViews array with the given files removed. `fileViews` does not get mutated.
 * @param {array} fileViews Array of fileViews
 * @param {string} title Title of fileView to update
 * @param {array} filePaths Array of file @ids to remove
 * @returns {array} New fileViews array with updated fileView entry; null if no update possible
 */
const generateFileViewsMinusFiles = (fileViews, title, filePaths) => {
    // Find file view with the given title.
    const indexOfFileViewWithMatchingTitle = fileViews.findIndex((view) => view.title === title);
    if (indexOfFileViewWithMatchingTitle !== -1) {
        // Filter the files of the matching file view to only include those not in the given files.
        const fileViewWithMatchingTitle = fileViews[indexOfFileViewWithMatchingTitle];
        const filesWithGivenFilesRemoved = fileViewWithMatchingTitle.files.filter((file) => !filePaths.includes(file));

        // Build a new view object with the filtered array of files.
        const updatedView = {
            title: fileViewWithMatchingTitle.title,
            files: filesWithGivenFilesRemoved,
        };

        // Update view state with copies of existing files array before the updated
        // view, the updated view, and then the existing files array after the updated
        // view -- no mutation of existing arrays nor objects.
        return (
            fileViews
                .slice(0, indexOfFileViewWithMatchingTitle)
                .concat(updatedView, fileViews.slice(indexOfFileViewWithMatchingTitle + 1))
        );
    }
    return null;
};


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
                return { ...state, elements: state.elements.concat([action.elementAtId]) };
            }
            return state;
        case ADD_MULTIPLE_TO_CART:
            return { ...state, elements: mergeCarts(state.elements, action.elementAtIds) };
        case REMOVE_FROM_CART: {
            const doomedIndex = state.elements.indexOf(action.elementAtId);
            if (doomedIndex !== -1) {
                const viewsWithUpdatedView = generateFileViewsMinusFiles(state.fileViews, action.title, action.filePaths);
                return {
                    ...state,
                    elements: state.elements
                        .slice(0, doomedIndex)
                        .concat(state.elements.slice(doomedIndex + 1)),
                    fileViews: viewsWithUpdatedView || state.fileViews,
                };
            }
            return state;
        }
        case REMOVE_MULTIPLE_FROM_CART: {
            const viewsWithUpdatedView = generateFileViewsMinusFiles(state.fileViews, action.title, action.filePaths);
            return {
                ...state,
                elements: _.difference(state.elements, action.elementAtIds),
                fileViews: viewsWithUpdatedView || state.fileViews,
            };
        }
        case CLEAR_CART:
            return {
                ...state,
                elements: [],
                fileViews: [],
            };
        case REPLACE_CART:
            return { ...state, elements: action.elementAtIds };
        case CACHE_SAVED_CART:
            return { ...state, savedCartObj: action.savedCartObj };
        case CART_OPERATION_IN_PROGRESS:
            return { ...state, inProgress: action.inProgress };
        case DISPLAY_ALERT:
            return { ...state, alert: action.alert };
        case SET_NAME:
            return { ...state, name: action.name };
        case SET_IDENTIFIER:
            return { ...state, identifier: action.identifier };
        case SET_LOCKED:
            return { ...state, locked: action.locked };
        case SET_CURRENT:
            return { ...state, current: action.current };
        case SET_STATUS:
            return { ...state, status: action.status };
        case ADD_FILE_VIEW: {
            let stateFileViews = state.fileViews;
            if (!stateFileViews) {
                // No existing `file_views` property, so create a new object.
                stateFileViews = [];
            }
            const matchingFileView = stateFileViews.find((view) => view.title === action.title);
            if (!matchingFileView) {
                return { ...state, fileViews: stateFileViews.concat({ title: action.title, files: [] }) };
            }
            return state;
        }
        case REMOVE_FILE_VIEW:
            return { ...state, views: state.fileViews.filter((view) => view.title !== action.title) };
        case ADD_TO_FILE_VIEW: {
            // Only add the file when we find a view with a matching title, and that view doesn't
            // already have the new file.
            const viewIndex = state.fileViews.findIndex((view) => view.title === action.title);
            if (viewIndex !== -1) {
                const view = state.fileViews[viewIndex];
                const filesNotAlreadyInView = action.files.filter((newFile) => !view.files.includes(newFile));
                if (filesNotAlreadyInView.length > 0) {
                    // At least one file doesn't exist in matching view; add them and make an
                    // updated view entry.
                    const updatedView = {
                        title: view.title,
                        files: view.files.concat(filesNotAlreadyInView),
                    };

                    // Update view state with copies of existing files array before the updated
                    // view, the updated view, and then the existing files array after the updated
                    // view -- no mutation of existing arrays nor objects.
                    const viewsWithUpdatedView = state.fileViews.slice(0, viewIndex).concat(updatedView, state.fileViews.slice(viewIndex + 1));
                    return { ...state, fileViews: viewsWithUpdatedView };
                }
            }
            return state;
        }
        case REMOVE_FROM_FILE_VIEW: {
            const viewsWithUpdatedView = generateFileViewsMinusFiles(state.fileViews, action.title, action.files);
            if (viewsWithUpdatedView) {
                return { ...state, fileViews: viewsWithUpdatedView };
            }
            return state;
        }
        case REPLACE_FILE_VIEWS:
            return { ...state, fileViews: action.fileViews };
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
    return { ...cart, elements: mergedElements };
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
        /** Currently configured file views */
        fileViews: [],
        /** @id of current cart */
        current: '',
        /** Cache of saved cart */
        savedCartObj: {},
        /** Indicates cart operations currently in progress */
        inProgress: false,
        /** React component of alert to display */
        alert: null,
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
    CartAlert,
    CartBatchDownload,
    cartCacheSaved,
    CartClear,
    cartCreateAutosave,
    CartFileViewToggleComponent,
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
    getCartSearchTypes,
    getIsCartSearch,
    CART_MAX_ELEMENTS,
};


contentViews.register(Cart, 'cart-view'); // /cart-view/ URI
contentViews.register(Cart, 'Cart'); // /carts/<uuid> URI
contentViews.register(CartManager, 'cart-manager'); // /cart-manager/ URI
