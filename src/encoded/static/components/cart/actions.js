/**
 * Redux and thunk functions to interact with the cart in the Redux store.
 */
import cartCacheSaved from './cache_saved';
import cartSave, { cartUpdate } from './database';
import cartSetOperationInProgress from './in_progress';
import { cartGetSettings, cartSetSettingsCurrent } from './settings';


// Actions to use with Redux store.dispatch().
export const ADD_TO_CART = 'ADD_TO_CART';
export const ADD_MULTIPLE_TO_CART = 'ADD_MULTIPLE_TO_CART';
export const REMOVE_FROM_CART = 'REMOVE_FROM_CART';
export const REMOVE_MULTIPLE_FROM_CART = 'REMOVE_MULTIPLE_FROM_CART';
export const CLEAR_CART = 'CLEAR_CART';
export const REPLACE_CART = 'REPLACE_CART';
export const CACHE_SAVED_CART = 'CACHE_SAVED_CART';
export const CART_OPERATION_IN_PROGRESS = 'CART_OPERATION_IN_PROGRESS';
export const DISPLAY_ALERT = 'DISPLAY_ALERT';
export const SET_CURRENT = 'SET_CURRENT';
export const SET_NAME = 'SET_NAME';
export const SET_IDENTIFIER = 'SET_IDENTIFIER';
export const SET_LOCKED = 'SET_LOCKED';
export const SET_STATUS = 'SET_STATUS';
export const SET_DESCRIPTION = 'SET_DESCRIPTION';
export const ADD_FILE_VIEW = 'ADD_FILE_VIEW';
export const REMOVE_FILE_VIEW = 'REMOVE_FILE_VIEW';
export const ADD_TO_FILE_VIEW = 'ADD_TO_FILE_VIEW';
export const REMOVE_FROM_FILE_VIEW = 'REMOVE_FROM_FILE_VIEW';
export const REPLACE_FILE_VIEWS = 'REPLACE_FILE_VIEWS';
export const NO_ACTION = 'NO_ACTION';


/**
 * Redux action creator to add an element to the cart.
 * @param {string} elementAtId `@id` of element being added to cart
 * @return {object} Redux action object
 */
export const addToCart = (elementAtId) => (
    { type: ADD_TO_CART, elementAtId }
);


/**
 * Redux thunk action creator to add an element to the cart and save this change to the logged-in
 * user's cart object in the database.
 * @param {string} elementAtId `@id` of element being added to cart
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null if not logged in
 */
export const addToCartAndSave = (elementAtId, fetch) => (
    (dispatch, getState) => {
        dispatch(addToCart(elementAtId));
        const { elements, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartSave(elements, null, savedCartObj, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            cartCacheSaved(updatedSavedCartObj, dispatch);
            return updatedSavedCartObj;
        });
    }
);


/**
 * Redux action creator to add multiple elements to the cart.
 * @param {array} elementAtIds `@ids` of elements being added to cart
 * @return {object} Redux action object
 */
export const addMultipleToCart = (elementAtIds) => (
    { type: ADD_MULTIPLE_TO_CART, elementAtIds }
);


/**
 * Redux thunk action creator to add multiple elements to the cart and save this change to the
 * logged-in user's cart object in the database.
 * @param {array} elementAtIds `@ids` of elements being added to cart
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null not logged in
 */
export const addMultipleToCartAndSave = (elementAtIds, fetch) => (
    (dispatch, getState) => {
        dispatch(addMultipleToCart(elementAtIds));
        const { elements, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartSave(elements, null, savedCartObj, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            cartCacheSaved(updatedSavedCartObj, dispatch);
            return updatedSavedCartObj;
        });
    }
);


/**
 * Manually set the cart state to show an operation is in progress or not. This mostly gets set
 * automatically when other operations are performed. Use this to set it for other reasons.
 * @param {boolean} operationInProgress True to set operation in progress
 * @returns {object} Promise from initiating the operation; probably instantaneous
 */
export const cartManualSetOperationInProgress = (operationInProgress) => (
    (dispatch) => {
        cartSetOperationInProgress(operationInProgress, dispatch);
    }
);


/**
 * Redux action creator to remove an element from the cart.
 * @param {string} elementAtId `@id` of element to remove from the cart
 * @param {string} title Title of current file view
 * @param {array} filePaths All files in the given element
 * @return {object} Redux action object
 */
export const removeFromCart = (elementAtId, title, filePaths) => (
    { type: REMOVE_FROM_CART, elementAtId, title, filePaths }
);


/**
 * Redux thunk action creator to remove an element from the cart and save this change to the
 * logged-in user's cart object in the database.
 * @param {string} element Element being removed from cart
 * @param {string} title Title of current file view
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null not logged in
 */
export const removeFromCartAndSave = (element, title, fetch) => (
    (dispatch, getState) => {
        // Get the paths of all files, if any, within the given element.
        const filePaths = element.files ? element.files.map((file) => file['@id']) : [];

        dispatch(removeFromCart(element['@id'], title, filePaths));
        const { elements, fileViews, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartSave(elements, fileViews, savedCartObj, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            cartCacheSaved(updatedSavedCartObj, dispatch);
            return updatedSavedCartObj;
        });
    }
);


/**
 * Redux action creator to remove multiple elements from the cart.
 * @param {array} elementAtIds `@ids` of elements to remove from the cart
 * @param {string} title Title of current file view
 * @param {array} filePaths All files in the given elements
 * @return {object} Redux action object
 */
export const removeMultipleFromCart = (elementAtIds, title, filePaths) => (
    { type: REMOVE_MULTIPLE_FROM_CART, elementAtIds, title, filePaths }
);


/**
 * Redux thunk action creator to remove multiple elements from the cart and save this change to the
 * database.
 * @param {array} elements elements to remove from the cart
 * @param {string} title Title of current file view
 * @param {function} fetch fetch function from <App> context
 * @return {object} Promise from saving the cart; null if not logged in
 */
export const removeMultipleFromCartAndSave = (elements, title, fetch) => (
    (dispatch, getState) => {
        // Convert the given element objects to their element paths, and extract an array of paths
        // of all the files within all the elements.
        const elementPaths = elements.map((element) => element['@id']);
        const filePaths = elements.reduce((accFilePaths, element) => (
            element.files ? accFilePaths.concat(element.files.map((file) => file['@id'])) : accFilePaths
        ), []);

        dispatch(removeMultipleFromCart(elementPaths, title, filePaths));
        const { elements: updatedElementPaths, fileViews: updatedFileViews, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartSave(updatedElementPaths, updatedFileViews, savedCartObj, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            cartCacheSaved(updatedSavedCartObj, dispatch);
            return updatedSavedCartObj;
        });
    }
);


/**
 * Redux action creator to replace all items in the cart with another set of items.
 * @param {array} elementAtIds `@ids` of elements to set the cart to
 * @return {object} Redux action object
 */
export const replaceCart = (elementAtIds) => (
    { type: REPLACE_CART, elementAtIds }
);


/**
 * Redux action creator to cache a saved cart object into the cart store.
 * @param {object} savedCartObj Cart object as saved to the database
 * @return {object} Redux action object
 */
export const cacheSavedCart = (savedCartObj) => (
    { type: CACHE_SAVED_CART, savedCartObj }
);


/**
 * Redux action creator to indicate that a cart operation is currently in progress.
 * @param {bool} inProgress True to indicate cart operation in progress; false when done
 * @return {object} Redux action object
 */
export const cartOperationInProgress = (inProgress) => (
    { type: CART_OPERATION_IN_PROGRESS, inProgress }
);


/**
 * Redux action creator to indicate that <App> should display the given cart-related alert (in the
 * form of a React component). The component that renders the alert should normally wrap it in the
 * libs/ui/modal.js components. This is useful for cart alerts that might not appear right away,
 * allowing the user to navigate to a different page before the alert appears. Alerts that you know
 * appear right away should simply display them in their own React components.
 * @param {object} alert React component to display alert modal
 *
 * @return {object} Redux action to display an alert.
 */
export const triggerAlert = (alert) => (
    { type: DISPLAY_ALERT, alert }
);


/**
 * Redux action creator to set the name of the cart.
 * @param {string} name Name to set cart to
 * @return {object} Redux action object
 */
export const setCartName = (name) => (
    { type: SET_NAME, name }
);


/**
 * Redux action creator to set the identifier of the cart.
 * @param {string} identifier Identifier to set cart to
 * @return {object} Redux action object
 */
export const setCartIdentifier = (identifier) => (
    { type: SET_IDENTIFIER, identifier }
);


/**
 * Redux action creator to set the locked status of the cart.
 * @param {bool} locked Cart lock status
 * @return {object} Redux action object
 */
export const setCartLocked = (locked) => (
    { type: SET_LOCKED, locked }
);


/**
 * Redux action creator to set the current cart. This sets the current cart in the Redux store
 * only -- this does not affect the cart settings in localstorage.
 * @param {string} current @id of cart to set as current
 * @return {object} Redux action object
 */
export const setCurrentCart = (current) => (
    { type: SET_CURRENT, current }
);


/**
 * Redux action creator to set the status of the cart.
 * @param {string} status New status for cart
 * @return {object} Redux action object
 */
export const setCartStatus = (status) => (
    { type: SET_STATUS, status }
);


/**
 * Redux action creator to set the cart description.
 * @param {string} description Description of cart
 */
export const setDescription = (description) => (
    { type: SET_DESCRIPTION, description }
);


/**
 * Redux action creator to add a new file view.
 * @param {string} title Name of the new file view
 * @returns {object} Redux action object
 */
export const addFileView = (title) => (
    { type: ADD_FILE_VIEW, title }
);


/**
 * Redux action creator to remove an existing file view.
 * @param {string} title Name of the file view to remove
 * @returns {object} Redux action object
 */
export const removeFileView = (title) => (
    { type: REMOVE_FILE_VIEW, title }
);


/**
 * Redux action creator to add files to the file view specified by the given title.
 * @param {string} title Name of file view to add to
 * @param {array} files File @ids to add to view files
 * @returns {object} Redux action object
 */
export const addToFileView = (title, files) => (
    { type: ADD_TO_FILE_VIEW, title, files }
);


/**
 * Redux action creator to remove files from the file view specified by the given title.
 * @param {string} title Name of file view to remove from
 * @param {array} files File @ids to add to view files
 * @returns {object} Redux action object
 */
export const removeFromFileView = (title, files) => (
    { type: REMOVE_FROM_FILE_VIEW, title, files }
);


/**
 * Redux action creator to replace all file views in the current cart with the given file views.
 * @param {array} fileViews Array of file views to replace the current cart file views with
 * @returns {object} Redux action object
 */
export const replaceFileViews = (fileViews) => (
    { type: REPLACE_FILE_VIEWS, fileViews }
);


/**
 * Redux thunk action creator to add a new empty file view and save the updated cart to the
 * database.
 * @param {string} title Name of the new file view
 * @param {function} fetch fetch function from <App> context
 * @returns {object} Promise from saving the cart object
 */
export const addFileViewAndSave = (title, fetch) => (
    (dispatch, getState) => {
        dispatch(addFileView(title));
        const { fileViews, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartUpdate(savedCartObj['@id'], { file_views: fileViews }, {}, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            dispatch(cacheSavedCart(updatedSavedCartObj));
        });
    }
);


/**
 * Redux thunk action creator to add files to the file view specified by the given name and save
 * the updated cart to the database.
 * @param {string} title Name of file view to add to
 * @param {array} files File @ids to add to view files
 * @param {function} fetch fetch function from <App> context
 * @returns {object} Promise from saving the cart object
 */
export const addToFileViewAndSave = (title, files, fetch) => (
    (dispatch, getState) => {
        const { fileViews: existingFileViews, savedCartObj } = getState();
        if (!existingFileViews || existingFileViews.length === 0) {
            dispatch(addFileView(title));
        }
        dispatch(addToFileView(title, files));
        const { fileViews: updatedFileViews } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartUpdate(savedCartObj['@id'], { file_views: updatedFileViews }, {}, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            dispatch(cacheSavedCart(updatedSavedCartObj));
        });
    }
);


/**
 * Redux thunk action creator to remove files from the file view specified by the given name, and
 * save the updated cart to the database.
 * @param {string} title Name of file view to remove from
 * @param {array} files File @ids to remove from file views
 * @param {function} fetch fetch function from <App> context
 * @returns {object} Promise from saving the cart object
 */
export const removeFromFileViewAndSave = (title, files, fetch) => (
    (dispatch, getState) => {
        dispatch(removeFromFileView(title, files));
        const { fileViews: updatedFileViews, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartUpdate(savedCartObj['@id'], { file_views: updatedFileViews }, {}, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            dispatch(cacheSavedCart(updatedSavedCartObj));
        });
    }
);


/**
 * Redux action creator to clear all contents of the cart.
 * @returns {object} Redux action object
 */
export const clearCart = () => (
    { type: CLEAR_CART }
);


/**
 * Redux thunk action creator to clear the cart of elements and file views, and to save the
 * cleared cart.
 * @param {function} fetch fetch function from <App> context
 * @returns {object} Promise from saving the cart object
 */
export const clearCartAndSave = (fetch) => (
    (dispatch, getState) => {
        dispatch(clearCart());
        const { elements, fileViews, savedCartObj } = getState();
        cartSetOperationInProgress(true, dispatch);
        return cartSave(elements, fileViews, savedCartObj, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);
            dispatch(cacheSavedCart(updatedSavedCartObj));
        });
    }
);


/**
 * Redux thunk action creator to set the name and/or identifier of a cart both in the Redux store
 * and the cart's database object.
 * @param {string} {name} Name to assign to cart (optional)
 * @param {string} {identifier} Identifier (URI) to assign to cart (optional)
 * @param {object} cart Cart object being updated
 * @param {object} user Current user object, often from `session` React context variable
 * @param {func} fetch System fetch function
 * @return {Promise} Resolves to the updated cart object
 */
export const setCartNameIdentifierAndSave = ({ name, identifier }, cart, user, fetch) => (
    (dispatch) => (
        new Promise((resolve, reject) => {
            const nameIdentifierSetList = { name };

            // Determine whether the cart identifier needs to be set or removed from the cart
            // object entirely.
            let identifierRemovalList;
            if (identifier) {
                nameIdentifierSetList.identifier = identifier;
                identifierRemovalList = null;
            } else {
                identifierRemovalList = ['identifier'];
            }

            // Attempt to update the cart database object.
            cartSetOperationInProgress(true, dispatch);
            return cartUpdate(cart['@id'], nameIdentifierSetList, identifierRemovalList, fetch).then((updatedSavedCartObj) => {
                // We know the update of the cart object in the database succeeded, so update the
                // cart Redux store as well.
                cartSetOperationInProgress(false, dispatch);
                const currentCartAtId = cartGetSettings(user).current;

                // If we updated the current cart, re-cache the cart object.
                if (updatedSavedCartObj['@id'] === currentCartAtId) {
                    dispatch(cacheSavedCart(updatedSavedCartObj));
                }

                // Update the name and identifier in the cart store.
                if (name) {
                    dispatch(setCartName(name));
                }
                dispatch(setCartIdentifier(identifier || null));

                // The current cart settings track the current cart's identifier, so that needs to
                // be updated if the identifier for the current cart gets updated.
                if (cart['@id'] !== updatedSavedCartObj['@id']) {
                    // At this point we know the identifier changed, but we don't know if that
                    // affects the current cart.
                    if (cart['@id'] === currentCartAtId) {
                        // The identifier changed AND it affects the current cart, so update the
                        // current cart settings and cart Redux store with the new identifier.
                        cartSetSettingsCurrent(user, updatedSavedCartObj['@id']);
                        dispatch(setCurrentCart(updatedSavedCartObj['@id']));
                    }
                }
                resolve(updatedSavedCartObj);
            }, (err) => {
                cartSetOperationInProgress(false, dispatch);
                reject(err);
            });
        })
    )
);


/**
 * Redux thunk action creator to set the lock state of a cart both in the Redux store and the cart's
 * database object.
 * @param {bool} locked New locked state of the cart
 * @param {object} cart Cart object being updated
 * @param {object} user Current user object, often from `session` React context variable
 * @param {func} fetch System fetch function
 * @return {Promise} Resolves to the updated cart object
 */
export const setCartLockAndSave = (locked, cart, user, fetch) => (
    (dispatch) => {
        cartSetOperationInProgress(true, dispatch);
        return cartUpdate(cart['@id'], { locked }, {}, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);

            // If we updated the current cart, set the new locked state in the in-memory cart
            // object and re-cache the cart object.
            const currentCartAtId = cartGetSettings(user).current;
            if (updatedSavedCartObj['@id'] === currentCartAtId) {
                dispatch(setCartLocked(updatedSavedCartObj.locked));
                dispatch(cacheSavedCart(updatedSavedCartObj));
            }
        });
    }
);


/**
 * Redux thunk action creator to set the status of a cart both in the Redux store and the cart's
 * database object.
 * @param {string} locked New status of the cart
 * @param {object} cart Cart object being updated
 * @param {object} user Current user object, often from `session` React context variable
 * @param {func} fetch System fetch function
 * @return {Promise} Resolves to the updated cart object
 */
export const setCartStatusAndSave = (status, cart, user, fetch) => (
    (dispatch) => {
        cartSetOperationInProgress(true, dispatch);
        return cartUpdate(cart['@id'], { status }, {}, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);

            // If we updated the current cart, set the new status in the in-memory cart
            // object and re-cache the cart object.
            const currentCartAtId = cartGetSettings(user).current;
            if (updatedSavedCartObj['@id'] === currentCartAtId) {
                dispatch(setCartStatus(updatedSavedCartObj.status));
                dispatch(cacheSavedCart(updatedSavedCartObj));
            }
        });
    }
);


/**
 * Redux thunk action creator to set the description of the specified cart both in the Redux store
 * and the cart's database object.
 * @param {string} description Description of cart to save in the specified cart
 * @param {object} cart Cart object being updated
 * @param {object} user Current user object, often from `session` React context variable
 * @param {function} fetch System fetch function
 * @returns {Promise} Resolves to the updated cart object
 */
export const setDescriptionAndSave = (description, cart, user, fetch) => (
    (dispatch) => {
        cartSetOperationInProgress(true, dispatch);
        return cartUpdate(cart['@id'], { description }, {}, fetch).then((updatedSavedCartObj) => {
            cartSetOperationInProgress(false, dispatch);

            // If we updated the current cart, set the new description in the in-memory cart
            // object and re-cache the cart object.
            const currentCartAtId = cartGetSettings(user).current;
            if (updatedSavedCartObj['@id'] === currentCartAtId) {
                dispatch(setDescription(updatedSavedCartObj.description));
                dispatch(cacheSavedCart(updatedSavedCartObj));
            }
        });
    }
);
