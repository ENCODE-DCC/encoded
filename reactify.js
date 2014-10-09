"use strict";

var reactTransform  = require('react-tools').transform;
var through         = require('through');

module.exports = function(file, options) {

  function transformer(source) {
    var opts = Object.create(options);
    opts.sourceFilename = file;
    return reactTransform(source, opts);
  }

  var data = '';
  function write(chunk) {
    return data += chunk;
  }

  function compile() {
    if (!file.match(/\.json$/)) {
      // jshint -W040
      try {
        data = transformer(data);
      } catch (error) {
        error.name = 'ReactifyError';
        error.message = file + ': ' + error.message;
        error.fileName = file;

        this.emit('error', error);
      }
    }
    this.queue(data);
    return this.queue(null);
    // jshint +W040
  }

  return through(write, compile);
};
