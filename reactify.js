"use strict";

var reactTransform  = require('react-tools').transform;
var through         = require('through');

module.exports = function(file, options) {

  function transformer(source) {
    return reactTransform(source, options);
  }

  var data = '';
  function write(chunk) {
    return data += chunk;
  }

  function compile() {
    // jshint -W040
    try {
      var transformed = transformer(data);
      this.queue(transformed);
    } catch (error) {
      error.name = 'ReactifyError';
      error.message = file + ': ' + error.message;
      error.fileName = file;

      this.emit('error', error);
    }
    return this.queue(null);
    // jshint +W040
  }

  return through(write, compile);
};
