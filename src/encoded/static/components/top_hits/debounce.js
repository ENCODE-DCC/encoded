/**
* This debounces the specified function by clearing the previous
* timerID (if any) and returning the new timerID. If the delay
* passes without the timer being reset then the function will fire.
* @param {function} func - The function to call after specified delay.
* @param {number} delay - Time in ms to wait before firing function.
* @param {number} timerId - Previous timeout to clear before setting new timeout.
* @return {number} The new timerID.
*/
const debounce = (func, delay, timerId) => {
    clearTimeout(timerId);
    return setTimeout(func, delay);
};


export default debounce;
