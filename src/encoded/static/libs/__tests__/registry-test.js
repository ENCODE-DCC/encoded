'use strict';

jest.dontMock('../registry');
jest.dontMock('underscore');
var Registry = require('../registry');

var test_obj = {'@type': ['Test', 'Item']};
var specific_obj = {'@type': ['Specific', 'Item']};
var other_obj = {'@type': ['Other']};

var views = [
    {for_: 'Item'},
    {for_: 'Specific'},
    {name: 'named', for_: 'Item'}
];

var make_one = function () {
    var registry = new Registry();
    views.forEach(function (view) {
        registry.register(view, view.for_, view.name);
    });
    registry.fallback = function () {
        return {fallback: true};
    };
    return registry;
};

describe("The registry library", function() {

    it("is able to lookup views for item in order of specificity", function() {
        var registry = make_one();
        expect(registry.lookup(test_obj).for_).toBe('Item');
        expect(registry.lookup(specific_obj).for_).toBe('Specific');
    });

    it("is able to lookup named views for item", function() {
        var registry = make_one();
        expect(registry.lookup(test_obj, 'named').name).toBe('named');
    });

    it("is able to fallback to view for objects with unknown types", function() {
        var registry = make_one();
        expect(registry.lookup(other_obj).fallback).toBe(true);
    });

});
