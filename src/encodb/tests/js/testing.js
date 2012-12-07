// Signame main.js to avoid application startup. It is included to avoid
// duplicating requirejs configuration.
var TESTRUNNER = true;

requirejs.config({
    baseUrl: '/static',

    paths: {
        jquery: 'libs/jquery.min',
        // Jasmine
        jasmine: '/tests/js/libs/jasmine/jasmine',
        jasmine_html: '/tests/js/libs/jasmine/jasmine-html'
    },

    shim: {
        jasmine: {
            exports: 'jasmine'
        },

        jasmine_html: {
            deps: ['jasmine']
        }
    }
});

require(['jquery', 'jasmine', 'jasmine_html', 'main',
    '/tests/js/specs/testing_spec.js'],
function ($, jasmine) {
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
