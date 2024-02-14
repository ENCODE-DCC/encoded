const gulp = require('gulp');
const log = require('fancy-log');
const webpack = require('webpack');

const setProduction = (cb) => {
    process.env.NODE_ENV = 'production';
    if (cb) {
        cb();
    }
};

const webpackOnBuild = done => (err, stats) => {
    if (err) {
        throw new log.error(err);
    }
    log(stats.toString({
        colors: true,
        excludeAssets: [/.*ckeditor.*/],
    }));
    if (done) {
        done(err);
    }
};

const webpackSetup = (cb) => {
    const webpackConfig = require('./webpack.config.js');
    webpack(webpackConfig).run(webpackOnBuild(cb));
};

const watch = (cb) => {
    const webpackConfig = require('./webpack.config.js');
    webpack(webpackConfig).watch(300, webpackOnBuild(cb));
};

const series = gulp.series;

gulp.task('default', series(webpackSetup, watch));
gulp.task('dev', series('default'));
gulp.task('build', series(setProduction, webpackSetup));
