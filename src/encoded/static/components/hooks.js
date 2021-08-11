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
