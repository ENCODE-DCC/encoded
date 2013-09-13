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
            var origin = document.location.origin;
            if (typeof origin === 'undefined') {
                // Older Firefox
                origin = document.location.protocol  + '//' + document.location.host;
            }
            expect(uri.href).toBe(origin + '/search?q=devmo#test');
            expect(uri.origin).toBe(origin);
            expect(uri.pathname).toBe('/search');
            expect(uri.port).toBe(document.location.port);
            expect(uri.protocol).toBe(document.location.protocol);
            expect(uri.search).toBe('?q=devmo');
            expect(uri.params().q).toBe('devmo');
        });

        it("is able to parse the current document uri", function() {
            var uri = URI();
            expect(uri.hash).toBe(document.location.hash);
            expect(uri.host).toBe(document.location.host);
            expect(uri.hostname).toBe(document.location.hostname);
            var origin = document.location.origin;
            if (typeof origin === 'undefined') {
                // Older Firefox
                origin = document.location.protocol  + '//' + document.location.host;
            }
            expect(uri.href).toBe(document.location.href);
            expect(uri.origin).toBe(origin);
            expect(uri.pathname).toBe(document.location.pathname);
            expect(uri.port).toBe(document.location.port);
            expect(uri.protocol).toBe(document.location.protocol);
            expect(uri.search).toBe(document.location.search);
        });

        it("is able calculate correct sameOrigin on http URIs.", function() {
            // XXX review https://developer.mozilla.org/en-US/docs/Same-origin_policy_for_file:_URIs
            var uri = URI(example_uri);
            expect(uri.sameOrigin('http://www.example.com:8080/bar')).toBe(true);
            expect(uri.sameOrigin('http://www.example.com:8080/')).toBe(true);
            expect(uri.sameOrigin('http://www.example.com:8081/')).toBe(false);
            expect(uri.sameOrigin('http://www.example.com/')).toBe(false);
            expect(uri.sameOrigin('https://www.example.com/')).toBe(false);
        });

        it("is able to parse file URIs", function() {
            var uri = URI('file:///search?q=devmo#test');
            expect(uri.hash).toBe('#test');
            expect(uri.host).toBe('');
            expect(uri.hostname).toBe('');
            expect(uri.href).toBe('file:///search?q=devmo#test');
            expect(uri.origin).toBe('file://');
            expect(uri.pathname).toBe('/search');
            expect(uri.port).toBe('');
            expect(uri.protocol).toBe('file:');
            expect(uri.search).toBe('?q=devmo');
            expect(uri.params().q).toBe('devmo');
        });

        it("is able calculate correct sameOrigin on file URIs.", function() {
            // XXX review https://developer.mozilla.org/en-US/docs/Same-origin_policy_for_file:_URIs
            var uri = URI('file:///search?q=devmo#test');
            expect(uri.sameOrigin('file:///search?q=devmo#bar')).toBe(true);
            expect(uri.sameOrigin('file:///search?a=1')).toBe(true);
            expect(uri.sameOrigin('file:///search')).toBe(true);
            expect(uri.sameOrigin('file:///foo')).toBe(false);
        });

        it("is able to parse data URIs", function() {
            var uri = URI('data:text/plain;charset=utf-8,foo?q=devmo#test');
            expect(uri.hash).toBe('');
            expect(uri.host).toBe('');
            expect(uri.hostname).toBe('');
            expect(uri.href).toBe('data:text/plain;charset=utf-8,foo?q=devmo#test');
            expect(uri.origin).toBe('null');
            expect(uri.pathname).toBe('');
            expect(uri.port).toBe('');
            expect(uri.protocol).toBe('data:');
            expect(uri.search).toBe('');
            expect(uri.params().q).toBe(undefined);
        });

        it("is able calculate correct sameOrigin on data URIs.", function() {
            // XXX review https://developer.mozilla.org/en-US/docs/Same-origin_policy_for_file:_URIs
            var href = 'data:text/plain;charset=utf-8,foo?q=devmo#test';
            expect(URI(href).sameOrigin(href)).toBe(false);
        });

        it("is able to parse params with multiple spaces", function() {
            var uri = URI('/search?q=devmo++');
            expect(uri.params().q).toBe('devmo  ');
		});

    });

});
