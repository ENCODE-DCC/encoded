define(['jquery', 'underscore', 'jsx!app', 'jasmine'],
function testing_spec($, _, app) {

    describe("The testing setup", function() {
        it("is able to import the application", function() {
            expect(_.isObject(app)).toBe(true);
        });
    });

});
