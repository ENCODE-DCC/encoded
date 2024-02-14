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
import { contentViews, listingViews } from '../globals';
import cartAddElements from './add_elements';
import CartAlert from './cart_alert';
import { CartAddAllSearch, CartAddAllElements } from './add_multiple';
import cartCacheSaved from './cache_saved';
import CartBatchDownload from './batch_download';
import Cart, { CartStaticDisplayList } from './cart';
import CartClear from './clear';
import CartFileViewToggleComponent from './file_view';
import cartSetOperationInProgress from './in_progress';
import CartMergeShared from './merge_shared';
import cartRemoveElements from './remove_elements';
import cartSave, { cartCreateAutosave, cartRetrieve } from './database';
import CartManager from './manager';
import CartMenu from './menu';
import cartSetCurrent from './set_current';
import CartSearchControls from './search_controls';
import CartSearchListing from './search_listing';
import { cartGetSettings, cartSetSettingsCurrent } from './settings';
import CartShare from './share';
import CartListedSwitch from './status';
import cartStore, { cartModule } from './store';
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


// Include any symbols needed outside the "cart" directory.
export {
    CartAddAllSearch,
    CartAddAllElements,
    CartAlert,
    CartBatchDownload,
    cartCacheSaved,
    CartClear,
    cartCreateAutosave,
    CartStaticDisplayList,
    CartFileViewToggleComponent,
    cartGetSettings,
    CartListedSwitch,
    cartSetSettingsCurrent,
    CartMergeShared,
    cartMergeElements,
    cartRemoveElements,
    cartRetrieve,
    cartSetOperationInProgress,
    CartSearchControls,
    cartSetCurrent,
    CartMenu,
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
listingViews.register(CartSearchListing, 'Cart');
