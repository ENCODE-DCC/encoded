define(['registry', 'jasmine'],
function (Registry) {

    var test_obj = {'@type': ['test', 'item']};
    var specific_obj = {'@type': ['specific', 'item']};
    var other_obj = {'@type': ['other']};

    var views = [
        {for_: 'item'},
        {for_: 'specific'},
        {name: 'named', for_: 'item'}
    ];

    var make_one = function () {
        var registry = Registry();
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
            expect(registry.lookup(test_obj).for_).toBe('item');
            expect(registry.lookup(specific_obj).for_).toBe('specific');
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

});
