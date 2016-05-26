var gulp = require('gulp');
var gutil = require('gulp-util');
var webpack = require('webpack');


gulp.task('default', ['webpack', 'watch']);
gulp.task('dev', ['default']);
gulp.task('build', ['set-production', 'webpack']);

gulp.task('set-production', [], function () {
  process.env.NODE_ENV = 'production';
});

var webpackOnBuild = function (done) {
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

gulp.task('webpack', [], function (cb) {
  var webpackConfig = require('./webpack.config.js');
  webpack(webpackConfig).run(webpackOnBuild(cb));
});

gulp.task('watch', [], function (cb) {
  var webpackConfig = require('./webpack.config.js');
  webpack(webpackConfig).watch(300, webpackOnBuild());
});
