'use strict';

// Require all components to ensure javascript load ordering
require('./antibody');
require('./app');
require('./image');
require('./biosample');
require('./collection');
require('./dataset');
require('./dbxref');
require('./errors');
require('./experiment');
require('./footer');
require('./globals');
require('./graph');
require('./home');
require('./item');
require('./page');
require('./mixins');
require('./navbar');
require('./platform');
require('./statuslabel');
require('./search');
require('./target');
require('./publication');
require('./pipeline');
require('./software');
require('./testing');
require('./edit');
require('./inputs');
require('./blocks');

module.exports = require('./app');
