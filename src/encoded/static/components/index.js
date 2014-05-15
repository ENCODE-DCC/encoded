/** @jsx React.DOM */
'use strict';

// Require all components to ensure javascript load ordering
require('./antibody');
require('./app');
require('./biosample');
require('./collection');
require('./dataset');
require('./dbxref');
require('./errors');
require('./experiment');
require('./footer');
require('./globals');
require('./home');
require('./item');
require('./page');
require('./mixins');
require('./navbar');
require('./platform');
require('./search');
require('./target');
require('./testing');
require('./edit');

module.exports = require('./app');
