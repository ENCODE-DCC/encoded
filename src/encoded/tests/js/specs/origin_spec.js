var origin = require('origin');

describe("The origin.same function", function() {

    var example_uri = 'http://www.example.com:8080/search?q=devmo#test';

    it("is able calculate correct origin.same on http URIs.", function() {
        var from = example_uri;
        expect(origin.same(from, 'http://www.example.com:8080/bar')).toBe(true);
        expect(origin.same(from, 'http://www.example.com:8080/')).toBe(true);
        expect(origin.same(from, 'http://www.example.com:8081/')).toBe(false);
        expect(origin.same(from, 'http://www.example.com/')).toBe(false);
        expect(origin.same(from, 'https://www.example.com/')).toBe(false);
        // https://bugzilla.mozilla.org/show_bug.cgi?id=296871
        expect(origin.same(from, 'data:text/plain;charset=utf-8,foo?q=devmo#test')).toBe(true);
        expect(origin.same(from, 'javascript:alert("foo")')).toBe(true);
    });

    it("is able calculate correct origin.same on file URIs.", function() {
        // XXX review https://developer.mozilla.org/en-US/docs/Same-origin_policy_for_file:_URIs
        var from = 'file:///search?q=devmo#test';
        expect(origin.same(from, 'file:///search?q=devmo#bar')).toBe(true);
        expect(origin.same(from, 'file:///search?a=1')).toBe(true);
        expect(origin.same(from, 'file:///search')).toBe(true);
        expect(origin.same(from, 'file:///foo')).toBe(false);
    });

});
