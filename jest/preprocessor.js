'use strict';

// Use newer
var transform = require('jstransform').transform;
var visitors = require('react-tools/vendor/fbtransform/visitors');

module.exports = {
  process: function(src) {
    return transform(visitors.getAllVisitors(), src).code;
  }
};
