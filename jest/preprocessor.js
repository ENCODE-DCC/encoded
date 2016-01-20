'use strict';
var babel = require("babel-core");

var ignored = {
    'underscore.js': true,
    'moment.js': true,
    'immutable.js': true,
}

module.exports = {
  process: function (src, path) {
    if (path.slice(-5) === '.node') return '';
    if (path.slice(-3) !== '.js') return src;
    if (ignored[path.split('/').slice(-1)[0]]) return src;
    var stage = process.env.BABEL_JEST_STAGE || 2;

    if (babel.canCompile(path)) {
      return babel.transform(src, {
        filename: path,
        stage: stage,
        retainLines: true,
        auxiliaryCommentBefore: "istanbul ignore next"
      }).code;
    }

    return src;
  }
};