/**
* This debounces the specified function by clearing the previous
* timerID (if any) and returning the new timerID. If the delay
* passes without being reset then the function will fire.
*/
const debounce = (func, delay, timerId) => {
    clearTimeout(timerId);
    return setTimeout(func, delay);
};

export default debounce;
