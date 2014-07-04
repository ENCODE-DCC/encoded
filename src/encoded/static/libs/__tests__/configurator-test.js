'use strict';

jest.dontMock('../configurator');

describe("The configurator library", function() {
    var config;

    beforeEach(function () {
        var Configurator = require('../configurator');
        config = new Configurator();
    });

    it("prevents an included function from being included more than once", function() {
        var included = jest.genMockFunction();
        config.include(included);
        config.include(included);
        expect(included.mock.calls.length).toBe(1);
    });

    it("prevents an included module from being included more than once", function() {
        var simple = {
            includeme: jest.genMockFunction()
        };

        config.include(simple);
        config.include(simple);
        config.include(simple.includeme);
        expect(simple.includeme.mock.calls.length).toBe(1);
    });

    it("allows for circular includes", function() {
        var module1 = {
            includeme: jest.genMockFunction().mockImplementation(function (config) {
                config.include(module2);
            })
        };

        var module2 = {
            includeme: jest.genMockFunction().mockImplementation(function (config) {
                config.include(module1);
            })
        };

        config.include(module1);
        expect(module1.includeme.mock.calls.length).toBe(1);
        expect(module2.includeme.mock.calls.length).toBe(1);
    });

});
