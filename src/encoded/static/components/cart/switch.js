import {
    cacheSavedCart,
    replaceCart,
    setCartIdentifier,
    setCartName,
    setCartStatus,
    setCurrentCart,
} from './actions';
import { cartRetrieve } from './database';


/**
 * Switch to a different cart, handling the Redux states to switch to and loading the newly current
 * cart.
 * @param {string} currentCartAtId @id of the cart that has become the current one.
 * @param {func} fetch - System fetch function
 */
const switchCart = (currentCartAtId, fetch) => (
    dispatch => (
        new Promise((resolve, reject) => (
            cartRetrieve(currentCartAtId, fetch).then((savedCartObj) => {
                dispatch(setCurrentCart(currentCartAtId));
                dispatch(replaceCart(savedCartObj.elements));
                dispatch(setCartName(savedCartObj.name));
                dispatch(setCartIdentifier(savedCartObj.identifier));
                dispatch(setCartStatus(savedCartObj.status));
                dispatch(cacheSavedCart(savedCartObj));
                resolve(savedCartObj);
            }, (err) => {
                reject(err);
            })
        ))
    )
);

export default switchCart;
