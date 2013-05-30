define(function () {
    'use strict';

    function AssertionError(message) {
        this.name = this.constructor.name; //set our function's name as error name.
        this.message = message;
    }

    AssertionError.prototype = new Error();
    AssertionError.prototype.constructor = AssertionError;

    function assert(value, message) {
        if (!value) throw new AssertionError(message);
    }

    assert.AssertionError = AssertionError;

    return assert;
});
