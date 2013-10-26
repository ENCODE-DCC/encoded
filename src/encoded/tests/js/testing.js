var domready = require('domready');

domready(function ready() {
    var jasmineEnv = jasmine.getEnv();
    jasmineEnv.updateInterval = 1000;
    var htmlReporter = new jasmine.HtmlReporter();
    jasmineEnv.addReporter(htmlReporter);
    jasmineEnv.specFilter = function(spec) {
         return htmlReporter.specFilter(spec);
    };
    jasmineEnv.execute();
});
