/* global __dirname */
const React = require('react');
const ReactDOMServer = require('react-dom/server');
const transformResponse = require('subprocess-middleware').transformResponse;
const fs = require('fs');
const path = require('path');

// Retrieve the file containing webpack build statistics and get the generated CSS hashed file
// names so we can later write it to the <link rel="stylesheet"> tag.
const buildFiles = JSON.parse(fs.readFileSync(path.join(__dirname, '/../build/stats.json'))).assetsByChunkName.style;
const doctype = '<!DOCTYPE html>\n';
const inline = fs.readFileSync(path.join(__dirname, '/../build/inline.js')).toString();

function render(Component, body, res) {
    // Search for the hashed CSS file name in the buildFiles list
    const cssFile = buildFiles.find(file => !!file.match(/^\.\/css\/style(\.[0-9a-z]+){0,1}\.css$/));
    const context = JSON.parse(body);
    const props = {
        context: context,
        href: res.getHeader('X-Request-URL') || context['@id'],
        inline: inline,
        styles: `/static/build/${cssFile}`,
    };
    let markup;
    try {
        markup = ReactDOMServer.renderToString(<Component {...props} />);
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
            context: context,
        };
        // To debug in browser, pause on caught exceptions:
        //   app.setProps({context: app.props.context.context})
        res.statusCode = 500;
        markup = ReactDOMServer.renderToString(<Component {...props} />);
    }
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    return new Buffer(doctype + markup);
}


module.exports.build = function (Component) {
    return transformResponse(render.bind(null, Component));
};
