var React = require('react');
var streams = require('./streams');

module.exports.run = function run(Component, options) {
    // Pass process to avoid browserify problems
    options = options || {};
    var doctype = options.doctype || '<!DOCTYPE html>';
    doctype += '\n';    

    // Avoid browserify
    var stdin = options.stdin || eval('process.stdin');
    var stdout = options.stdout || eval('process.stdout');

    var render = function(props) {
        //var component = module(props);
        var component = Component(props);
        var markup;
        React.renderComponentToString(component, function(m) {
            markup = m;
        });
        return doctype + markup;
    };


    var strings = streams.DelimitedStream({delimiter: '\0'});
    var json_objects = streams.SimpleTransform({transform: JSON.parse})
    var render = streams.SimpleTransform({transform: render});
    var output_length = streams.OutputLength();
    var error_output_length = streams.OutputLength({result_type: 'ERROR'});

    // Start reading from stdin so we don't exit.
    stdin.resume();

    var log = console._stdout = console._stderr = streams.StringIO();

    stdin.pipe(strings);
    strings.pipe(json_objects);
    json_objects.pipe(render);
    render.pipe(output_length);
    render.on('error_result', function (err) {
        error_output_length.write(err.stack + '\n--\n' + log.getValue());
    });
    output_length.pipe(stdout);
    output_length.on('data', log.clear.bind(log));
    error_output_length.pipe(stdout);
    error_output_length.on('data', log.clear.bind(log));
};
