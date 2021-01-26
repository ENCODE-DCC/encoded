/**
* This debounces the specified function by clearing the previous
* timerID (if any) and returning the new timerID. If the delay
* passes without the timer being reset then the function will fire.
*/
const debounce = (func, delay, timerId) => {
    clearTimeout(timerId);
    return setTimeout(func, delay);
};

export default debounce;
