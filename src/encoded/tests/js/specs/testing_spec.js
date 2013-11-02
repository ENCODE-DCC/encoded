var _ = require('underscore');
var encoded = require('main');

    describe("The testing setup", function() {
        it("is able to import the application", function() {
            expect(_.isObject(encoded.App)).toBe(true);
        });
    });
