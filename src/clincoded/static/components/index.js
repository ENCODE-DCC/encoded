'use strict';

// Require all components to ensure javascript load ordering
require('./app');
require('./image');
require('./collection');
require('./dbxref');
require('./errors');
require('./gene');
require('./footer');
require('./globals');
require('./home');
require('./item');
require('./page');
require('./mixins');
require('./navigation');
require('./statuslabel');
require('./search');
require('./publication');
require('./curator');
require('./testing');
require('./edit');
require('./inputs');

module.exports = require('./app');
