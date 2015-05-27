'use strict';
var React = require('react');
var doctype = '<!DOCTYPE html>\n';
var transformResponse = require('subprocess-middleware').transformResponse;
var fs = require('fs');
var inline = fs.readFileSync(__dirname + '/../build/inline.js').toString();

var render = function (Component, body, res) {
    //var start = process.hrtime();
    var context = JSON.parse(body);
    var props = {
        context: context,
        href: res.getHeader('X-Request-URL') || context['@id'],
        inline: inline
    };
    var markup;
    try {
        markup = React.renderToString(<Component {...props} />);
    } catch (err) {
        props.context = {
            '@type': ['RenderingError', 'error'],
            status: 'error',
            code: 500,
            title: 'Server Rendering Error',
            description: 'The server erred while rendering the page.',
            detail: err.stack,
            log: console._stdout.toString(),
            warn: console._stderr.toString(),
            context: context
        };
        // To debug in browser, pause on caught exceptions:
        //   app.setProps({context: app.props.context.context})
        res.statusCode = 500;
        markup = React.renderToString(<Component {...props} />);
    }
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    //var duration = process.hrtime(start);
    //res.setHeader('X-React-duration', duration[0] * 1e6 + (duration[1] / 1000 | 0));
    return new Buffer(doctype + markup);
};


module.exports.build = function (Component) {
    return transformResponse(render.bind(null, Component));
};
