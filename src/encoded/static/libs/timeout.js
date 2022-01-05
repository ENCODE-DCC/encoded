/**
 * Provides general timer services.
 *
 * Usage:
 * const foo = new Timeout(expirationCallback, delayInMilliseconds);
 *
 * Allocates a new timeout object without actually starting the timer. Pass it a function to call
 * after the delay, as well as the number of milliseconds to wait before calling this callback.
 *
 * foo.start(delayOverrideInMilliseconds);
 *
 * Use this to start the timer which, by default, expires when the delay set when allocating this
 * object has expired. If you want to set a different timeout delay just this time, you can
 * optionally pass in the number of milliseconds to delay to override the delay set when allocating
 * this object.
 *
 * foo.stop();
 *
 * Stops an in-progress timer so that the callback doesn't get called. Does nothing if you haven't
 * yet started the timer.
 *
 * foo.restart(delayOverrideInMilliseconds);
 *
 * Stops any in-progress timer and starts a new one, optionally overriding the delay set when you
 * allocated the timer.
 */


/**
 * Timeout functionality. Calls a function after a specified delay. The client can also stop or restart the timer.
 */
export default class Timeout {
    constructor(expiryCallback, delay) {
        this._expiryCallback = expiryCallback;
        this._delay = delay;
    }

    /**
     * Called when the timer expires to clear the timer data and call the user-provided callback.
     */
    _onExpiry() {
        this._timeout = null;
        this._expiryCallback();
    }

    /**
     * Starts the timeout counter if one is not already running.
     * @param {number} delayOverride - Delay to override the one set at initialization.
     */
    start(delayOverride) {
        if (!this._timeout) {
            this._timeout = setTimeout(this._onExpiry.bind(this), delayOverride || this._delay);
        }
    }

    /**
     * Stops the timeout counter if one is running.
     */
    stop() {
        if (this._timeout) {
            clearTimeout(this._timeout);
            this._timeout = null;
        }
    }

    /**
     * Stops any running timer and starts a new one.
     * @param {number} delayOverride - Delay to override the one set at initialization.
     */
    restart(delayOverride) {
        this.stop();
        this.start(delayOverride);
    }
}
