import Timeout from '../timeout';


jest.useFakeTimers();

describe('Timer class', () => {
    it('calls the callback after expriation', () => {
        const callback = jest.fn();
        const timer = new Timeout(callback, 1000);
        timer.start();
        expect(callback).not.toBeCalled();
        jest.runAllTimers();
        expect(callback).toBeCalled();
        expect(callback).toHaveBeenCalledTimes(1);
    });

    it('doesn\'t call the callback if stopped', () => {
        const callback = jest.fn();
        const timer = new Timeout(callback, 1000);
        timer.start();
        timer.stop();
        expect(callback).not.toBeCalled();
        jest.runAllTimers();
    });

    it('calls the callback after restarting', () => {
        const callback = jest.fn();
        const timer = new Timeout(callback, 1000);
        timer.start();
        expect(callback).not.toBeCalled();
        timer.restart();
        jest.runAllTimers();
        expect(callback).toBeCalled();
        expect(callback).toHaveBeenCalledTimes(1);
    });
});
