const debounce = (func, delay, timerId) => {
    clearTimeout(timerId);
    return setTimeout(func, delay);
};

export default debounce;
