/* global process, __dirname */
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const path = require('path');
const webpack = require('webpack');

const env = process.env.NODE_ENV;

const PATHS = {
    static: path.resolve(__dirname, 'src/encoded/static'),
    build: path.resolve(__dirname, 'src/encoded/static/build'),
    serverbuild: path.resolve(__dirname, 'src/encoded/static/build-server'),
    fonts: path.resolve(__dirname, 'src/encoded/static/font'),
    images: path.resolve(__dirname, 'src/encoded/static/img'),
};

const plugins = [];
// don't include momentjs locales (large)
plugins.push(new webpack.IgnorePlugin(/^\.\/locale$/, [/moment$/]));

// To get auth0 v11 to build correctly:
// https://github.com/felixge/node-formidable/issues/337#issuecomment-183388869
plugins.push(new webpack.DefinePlugin({ 'global.GENTLY': false }));

let chunkFilename = '[name].js';
let styleFilename = './css/[name].css';

if (env === 'production') {
    // uglify code for production
    plugins.push(new webpack.optimize.UglifyJsPlugin({ minimize: true }));

    // Set production version of React
    // https://stackoverflow.com/questions/37311972/react-doesnt-switch-to-production-mode#answer-37311994
    plugins.push(
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify(env),
            },
        })
    );

    // add chunkhash to chunk names for production only (it's slower)
    chunkFilename = '[name].[chunkhash].js';
    styleFilename = './css/[name].[chunkhash].css';
}

const loaders = [
    // add babel to load .js files as ES6 and transpile JSX
    {
        test: /\.js$/,
        include: [
            PATHS.static,
            path.resolve(__dirname, 'node_modules/dalliance'),
        ],
        loader: 'babel',
    },
    {
        test: /\.json$/,
        loader: 'json',
    },
    {
        test: /\.(jpg|png|gif)$/,
        loader: 'url?limit=25000',
        include: PATHS.images,
    },
    {
        test: /\.scss$/,
        loader: ExtractTextPlugin.extract('css!sass'),
    },
];

module.exports = [
    // for browser
    {
        context: PATHS.static,
        entry: {
            inline: './inline',
            style: './scss/style.scss',
        },
        output: {
            path: PATHS.build,
            publicPath: '/static/build/',
            filename: '[name].js',
            chunkFilename,
        },
        module: {
            loaders,
        },
        devtool: 'source-map',
        plugins: plugins.concat(
            // Add a browser-only plugin to extract Sass-compiled styles and place them into an
            // external CSS file
            new ExtractTextPlugin(styleFilename, {
                disable: false,
                allChunks: true,
            }),

            // Add a browser-only plugin executed when webpack is done with all transforms. it
            // writes minimal build statistics to the "build" directory that contains the hashed
            // CSS file names that the server can render into the <link rel="stylesheet"> tag.
            function writeWPStats() {
                this.plugin('done', (stats) => {
                    // Write hash stats to stats.json so we can extract the CSS hashed file name.
                    require('fs').writeFileSync(
                        path.join(PATHS.build, 'stats.json'),
                        JSON.stringify(stats.toJson({ hash: true }, 'none')));
                });
            }
        ),
        debug: true,
    },
    // for server-side rendering
    {
        entry: {
            renderer: './src/encoded/static/server.js',
        },
        target: 'node',
        // make sure compiled modules can use original __dirname
        node: {
            __dirname: true,
        },
        externals: [
            'brace',
            'brace/mode/json',
            'brace/theme/solarized_light',
            'd3',
            'dagre-d3',
            'chart.js',
            'dalliance',
            // avoid bundling babel transpiler, which is not used at runtime
            'babel-core/register',
        ],
        output: {
            path: PATHS.serverbuild,
            publicPath: '/static/build-server',
            filename: '[name].js',
            libraryTarget: 'commonjs2',
            chunkFilename,
        },
        module: {
            loaders,
        },
        devtool: 'source-map',
        plugins,
        debug: true,
    },
];
