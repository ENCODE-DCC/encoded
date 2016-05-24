'use strict';

// Require all components to ensure javascript load ordering
require('./lib');
require('./app');
require('./image');
require('./collection');
require('./errors');
require('./footer');
require('./globals');
require('./graph');
require('./doc');
require('./home');
require('./item');
require('./page');
require('./mixins');
require('./search');
require('./report');
require('./testing');
require('./edit');
require('./inputs');
require('./blocks');
require('./user');
require('./schema');


module.exports = require('./app');
