'use strict';

// Require all components to ensure javascript load ordering
require('./lib');
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
require('./doc');
require('./home');
require('./item');
require('./page');
require('./mixins');
require('./platform');
require('./statuslabel');
require('./search');
require('./report');
require('./matrix');
require('./talen');
require('./target');
require('./publication');
require('./pipeline');
require('./software');
require('./testing');
require('./edit');
require('./inputs');
require('./blocks');
require('./user');
require('./schema');
require('./region_search');


module.exports = require('./app');
