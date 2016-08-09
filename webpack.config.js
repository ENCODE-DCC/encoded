/*global process, __dirname */
var ExtractTextPlugin = require('extract-text-webpack-plugin');

var path = require('path');
var webpack = require('webpack');
var env = process.env.NODE_ENV;

var PATHS = {
    static: path.resolve(__dirname, 'src/encoded/static'),
    build: path.resolve(__dirname, 'src/encoded/static/build')
};

var plugins = [];
// don't include momentjs locales (large)
plugins.push(new webpack.IgnorePlugin(/^\.\/locale$/, [/moment$/]));
var chunkFilename = '[name].js';

if (env === 'production') {
    // uglify code for production
    plugins.push(new webpack.optimize.UglifyJsPlugin({minimize: true}));
    // add chunkhash to chunk names for production only (it's slower)
    chunkFilename = '[name].[chunkhash].js';
}

var preLoaders = [
    // Strip @jsx pragma in react-forms, which makes babel abort
    {
        test: /\.js$/,
        include: path.resolve(__dirname, 'node_modules/react-forms'),
        loader: 'string-replace',
        query: {
            search: '@jsx',
            replace: 'jsx'
        }
    }
];

var loaders = [
    // add babel to load .js files as ES6 and transpile JSX
    {
        test: /\.js$/,
        include: [
            path.resolve(__dirname, 'src/encoded/static'),
            path.resolve(__dirname, 'node_modules/react-forms')
        ],
        loader: 'babel'
    },
    {
        test: /\.json$/,
        loader: 'json'
    }
];

module.exports = [
    // for browser
    {
        context: PATHS.static,
        entry: {inline: './inline'},
        output: {
            path: PATHS.build,
            publicPath: '/static/build/',
            filename: '[name].js',
            chunkFilename: chunkFilename
        },
        module: {
            preLoaders: preLoaders,
            loaders: loaders
        },
        devtool: 'source-map',
        plugins: plugins,
        debug: true
    },
    // for server-side rendering
    {
        entry: {
            renderer: './src/encoded/static/server.js',
            style: './src/encoded/static/scss/style.scss'
        },
        target: 'node',
        // make sure compiled modules can use original __dirname
        node: {
            __dirname: true
        },
        externals: [
            'brace',
            'brace/mode/json',
            'brace/theme/solarized_light',
            'd3',
            'dagre-d3',
            // avoid bundling babel transpiler, which is not used at runtime
            'babel-core/register'
        ],
        output: {
            path: PATHS.build,
            filename: '[name].js',
            libraryTarget: 'commonjs2',
            chunkFilename: chunkFilename
        },
        module: {
            preLoaders: preLoaders,
            loaders: loaders.concat({
                test: /\.scss$/,
                loader: ExtractTextPlugin.extract('css!sass')
            })
        },
        devtool: 'source-map',
        plugins: plugins.concat(
            new ExtractTextPlugin("./src/encoded/static/css/[name].[chunkhash].css", {
                disable: false,
                allChunks: true
            }),

            // Add plugin executed when webpack is done with all transforms.
            function() {
                this.plugin('done', function(stats) {
                    // Write hash stats to stats.json so we can extract the CSS hashed file name.
                    require('fs').writeFileSync(
                        path.join(__dirname, 'stats.json'),
                        JSON.stringify(stats.toJson({hash: true}, 'none')));
                });
            }
        ),
        debug: true
    }
];
