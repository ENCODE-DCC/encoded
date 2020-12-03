// Require all components to ensure javascript load ordering
require('./lib');
require('./view_controls.js');
require('./app');
require('./award');
require('./image');
require('./cart');
require('./collection');
require('./datacolors');
require('./dbxref');
require('./errors');
require('./footer');
require('./globals');
require('./graph');
require('./doc');
require('./item');
require('./page');
require('./platform');
require('./facets');
require('./search');
require('./report');
require('./matrix_audit');
require('./publication');
require('./testing');
require('./edit');
require('./inputs');
require('./blocks');
require('./user');
require('./schema');
require('./summary');
require('./patient');
require('./experiment_series');
require('./surgery');
require('./pathology_report');
require('./biospecimen');
require('./biofile');
require('./biodataset');
require('./doc');
require('./bioexperiment');



module.exports = require('./app');
