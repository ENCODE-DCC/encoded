'use strict';
var ReactTools = require('react-tools');
module.exports = {
  process: function(src, path) {
    if (path.slice(-5) === '.node') return '';
    if (path.slice(-3) !== '.js') return src;
    return ReactTools.transform(src, {harmony: true, es5: true, stripTypes: true});
  }
};
