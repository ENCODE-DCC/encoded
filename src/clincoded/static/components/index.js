'use strict';

// Require all components to ensure javascript load ordering
require('./app');
require('./image');
require('./collection');
require('./dbxref');
require('./errors');
require('./footer');
require('./globals');
require('./home');
require('./item');
require('./page');
require('./mixins');
require('./statuslabel');
require('./search');
require('./publication');
require('./curator');
require('./curation_central');
require('./create_gene_disease');
require('./group_curation');
require('./testing');
require('./edit');
require('./inputs');

module.exports = require('./app');
