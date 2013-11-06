function run() {
    var React = require('react');
    var moduleName = process.argv[2] || 'main';
    var module = require(moduleName);
    var doctype = '<!DOCTYPE html>\n';

    var render = function(props) {
        //var component = module(props);
        var component = module(props);
        var markup;
        React.renderComponentToString(component, function(m) {
            markup = m;
        });
        return doctype + markup;
    };


    var streams = require('streams');
    var strings = streams.DelimitedStream({delimiter: '\0'});
    var json_objects = streams.SimpleTransform({transform: JSON.parse})
    var render = streams.SimpleTransform({transform: render});
    var output_length = streams.OutputLength();
    var error_output_length = streams.OutputLength({result_type: 'ERROR'});

    // Start reading from stdin so we don't exit.
    process.stdin.resume();

    var log = console._stdout = console._stderr = streams.StringIO();

    process.stdin.pipe(strings);
    strings.pipe(json_objects);
    json_objects.pipe(render);
    render.pipe(output_length);
    render.on('error_result', function (err) {
        error_output_length.write(err.stack);
    });
    output_length.pipe(process.stdout);
    output_length.on('data', log.clear.bind(log));
    error_output_length.pipe(process.stdout);
    error_output_length.on('data', log.clear.bind(log));
}
module.exports = run
//window = {};
run();
