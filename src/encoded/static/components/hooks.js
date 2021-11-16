import React from 'react';


/**
 * Call react useEffect just once
 *
 * @param {function} fn
 */
export const useMount = (fn) => React.useEffect(fn, []);


/**
 * Gets the previous value of a state.
 * @param {*} value
 * @returns {*} Previous value of the state
 */
export const usePrevious = (value) => {
    const ref = React.useRef();
    React.useEffect(() => {
        ref.current = value;
    });
    return ref.current;
};


/**
 * Analogous to useState, but sets new values in the browser's session storage, and recalls them.
 * Supply a key to identify the value in session storage.
 * @param {string} key - Identifier of the given session storage data
 * @param {*} initialValue - Initial value to set for the given key; including objects
 * @returns {array} - [
 *     0: Value retrieved from session storage
 *     1: Function to set new value in session storage
 * ]
 */
export const useSessionStorage = (key, initialValue) => {
    const [value, setValue] = React.useState(() => {
        const item = typeof window !== 'undefined' ? window.sessionStorage.getItem(key) : null;
        return item ? JSON.parse(item) : initialValue;
    });

    const setValueMethod = (valueToStore) => {
        setValue(valueToStore);
        window.sessionStorage.setItem(key, JSON.stringify(valueToStore));
    };

    return [value, setValueMethod];
};
