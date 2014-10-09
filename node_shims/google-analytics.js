'use strict';
/* global ga */
global.ga = global.ga || function () {
    (ga.q = ga.q || []).push(arguments);
};
ga.l = +new Date();
module.exports = global.ga;
