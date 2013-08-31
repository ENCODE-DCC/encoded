// Signal main.js to avoid application startup. It is included to avoid
// duplicating requirejs configuration.
var TESTRUNNER = true;

requirejs.config({
    baseUrl: '/static',

    paths: {
        jquery: 'vendor/jquery',
        // Jasmine
        jasmine: '/tests/js/vendor/jasmine/jasmine',
        jasmine_html: '/tests/js/vendor/jasmine/jasmine-html',
        jasmine_jquery: '/tests/js/vendor/jasmine-jquery'
    },

    shim: {
        jasmine: {
            exports: 'jasmine'
        },

        jasmine_html: {
            deps: ['jasmine']
        },

        jasmine_jquery: {
            deps: ['jasmine', 'jquery']
        }
    }
});

TESTS = [
    '/tests/js/specs/testing_spec.js',
    '/tests/js/specs/registry_spec.js',
    '/tests/js/specs/uri_spec.js'
];

require(['jquery', 'jasmine', 'jasmine_html', 'main'],
function ($, jasmine) {
    // Defer import until after main is loaded to avoid module loading errors.
    require(TESTS, function () {
        $(function ready() {
            var jasmineEnv = jasmine.getEnv();
            jasmineEnv.updateInterval = 1000;
            var htmlReporter = new jasmine.HtmlReporter();
            jasmineEnv.addReporter(htmlReporter);
            jasmineEnv.specFilter = function(spec) {
                 return htmlReporter.specFilter(spec);
            };
            jasmineEnv.execute();
        });
    });
});
