define(['uri', 'jasmine'],
function uri_spec(URI) {

    // example from https://developer.mozilla.org/en-US/docs/Web/API/window.location
    var example_uri = 'http://www.example.com:8080/search?q=devmo#test';
    var test_example_uri = function (uri) {
        expect(uri.hash).toBe('#test');
        expect(uri.host).toBe('www.example.com:8080');
        expect(uri.hostname).toBe('www.example.com');
        expect(uri.href).toBe('http://www.example.com:8080/search?q=devmo#test');
        expect(uri.origin).toBe('http://www.example.com:8080');
        expect(uri.pathname).toBe('/search');
        expect(uri.port).toBe('8080');
        expect(uri.protocol).toBe('http:');
        expect(uri.search).toBe('?q=devmo');
        expect(uri.params().q).toBe('devmo');
    };

    describe("The uri library", function() {
        it("is able to parse an absolute uri", function() {
            test_example_uri(URI(example_uri));
        });

        it("is able to parse relative to a base uri", function() {
            test_example_uri(URI('/search?q=devmo#test', example_uri));
            test_example_uri(URI('search?q=devmo#test', example_uri));
            test_example_uri(URI('?q=devmo#test', example_uri));
            test_example_uri(URI('#test', example_uri));
        });

        it("is able to parse relative to the current document", function() {
            var uri = URI('/search?q=devmo#test');
            expect(uri.hash).toBe('#test');
            expect(uri.host).toBe(document.location.host);
            expect(uri.hostname).toBe(document.location.hostname);
            expect(uri.href).toBe(document.location.origin + '/search?q=devmo#test');
            expect(uri.origin).toBe(document.location.origin);
            expect(uri.pathname).toBe('/search');
            expect(uri.port).toBe(document.location.port);
            expect(uri.protocol).toBe(document.location.protocol);
            expect(uri.search).toBe('?q=devmo');
            expect(uri.params().q).toBe('devmo');
        });

    });

});
