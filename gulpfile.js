const gulp = require('gulp');
const gutil = require('gulp-util');
const webpack = require('webpack');

const setProduction = function (cb) {
  process.env.NODE_ENV = 'production';
  if (cb) {
      cb();
  }
};

const webpackOnBuild = function (done) {
  return function (err, stats) {
    if (err) {
      throw new gutil.PluginError("webpack", err);
    }
    gutil.log("[webpack]", stats.toString({
      colors: true
    }));
    if (done) { done(err); }
  };
};

const webpackSetup = function (cb) {
  var webpackConfig = require('./webpack.config.js');
  webpack(webpackConfig).run(webpackOnBuild(cb));
};

const watch = function (cb) {
  var webpackConfig = require('./webpack.config.js');
  webpack(webpackConfig).watch(300, webpackOnBuild(cb));
};

const series = gulp.series; 

gulp.task('default', series(webpackSetup, watch));
gulp.task('dev', series('default'));
gulp.task('build', series(setProduction, webpackSetup));
