import debounce from '../debounce';


jest.useFakeTimers();


describe('debounce', () => {
    test('function only fires once', () => {
        const func = jest.fn();
        let timerId = null;
        for (let i = 0; i < 100; i += 1) {
            jest.advanceTimersByTime(100);
            timerId = debounce(
                func,
                200,
                timerId
            );
        }
        expect(func).toHaveBeenCalledTimes(0);
        jest.advanceTimersByTime(100);
        expect(func).toHaveBeenCalledTimes(0);
        jest.advanceTimersByTime(99);
        expect(func).toHaveBeenCalledTimes(0);
        jest.advanceTimersByTime(1);
        // 200 ms since last debounce call.
        expect(func).toHaveBeenCalledTimes(1);
    });
});
