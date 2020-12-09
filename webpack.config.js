/* global process, __dirname */
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const path = require('path');
const webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const CopyPlugin = require("copy-webpack-plugin");

const env = process.env.NODE_ENV;

const PATHS = {
    static: path.resolve(__dirname, 'src/encoded/static'),
    build: path.resolve(__dirname, 'src/encoded/static/build'),
    serverbuild: path.resolve(__dirname, 'src/encoded/static/build-server'),
    fonts: path.resolve(__dirname, 'src/encoded/static/font'),
    images: path.resolve(__dirname, 'src/encoded/static/img'),
    ckeditor_source: path.resolve(__dirname, "node_modules/ckeditor4"),
    ckeditor_dest: path.resolve(__dirname, "src/encoded/static/build/ckeditor"),
};

const plugins = [];

// To get auth0 v11 to build correctly:
// https://github.com/felixge/node-formidable/issues/337#issuecomment-183388869
plugins.push(new webpack.DefinePlugin({ 'global.GENTLY': false }));
plugins.push(
    new CopyPlugin({
        patterns: [
            {
                // Adapted from https://github.com/ckeditor/ckeditor4-webpack-template/blob/master/webpack.config.js
                from: '{ckeditor.js,config.js,contents.css,styles.js,adapters/**/*,lang/**/*,plugins/**/*,skins/**/*,vendor/**/*}',
                to: PATHS.ckeditor_dest,
                context: PATHS.ckeditor_source,
            },
        ],
    })
);

let chunkFilename = '[name].js';
let styleFilename = './css/[name].css';
let mode = 'development';
const optimization = {};

if (env === 'production') {
    optimization.minimize = true;
    optimization.minimizer = [
        new TerserPlugin({
            sourceMap: true,
        }),
        new OptimizeCSSAssetsPlugin({}),
    ];

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

    mode = 'production';
}

const rules = [
    {
        test: /\.js$/,
        include: [
            PATHS.static,
            path.resolve(__dirname, 'node_modules/dagre-d3'),
            path.resolve(__dirname, 'node_modules/superagent'),
        ],
        use: {
            loader: 'babel-loader',
            query: { compact: false },
        },
    },
    {
        test: /\.(jpg|png|gif)$/,
        include: PATHS.images,
        use: [
            {
                loader: 'url-loader',
                options: {
                    limit: 25000,
                },
            },
        ],
    },
    {
        test: /\.scss$/,
        use: [
            MiniCssExtractPlugin.loader,
            { loader: 'css-loader', options: { sourceMap: true } },
            { loader: 'sass-loader', options: { sourceMap: true } },
        ],
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
            rules,
        },
        devtool: 'source-map',
        mode,
        optimization,
        plugins: plugins.concat(
            // Add a browser-only plugin to extract Sass-compiled styles and place them into an
            // external CSS file
            new MiniCssExtractPlugin({
                filename: styleFilename,
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
            // avoid bundling babel transpiler, which is not used at runtime
            '@babel/register',
        ],
        output: {
            path: PATHS.serverbuild,
            publicPath: '/static/build-server',
            filename: '[name].js',
            libraryTarget: 'commonjs2',
            chunkFilename,
        },
        module: {
            rules,
        },
        devtool: 'source-map',
        mode,
        optimization,
        plugins,
    },
];
