// Require all components to ensure javascript load ordering
require('./lib');
require('./antibody');
require('./app');
require('./award');
require('./image');
require('./biosample');

require('./cart');
require('./collection');
require('./datacolors');
require('./dataset');
require('./dbxref');
require('./errors');
require('./experiment');
require('./genetic_modification');
require('./footer');
require('./globals');
require('./graph');
require('./doc');
require('./donor');
require('./file');
require('./item');
require('./page');
require('./platform');
require('./search');
require('./report');
require('./matrix');
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
require('./summary');
require('./region_search');
require('./gene');
require('./biosample_type');
require('./patient');
require('./experiment_series');
require('./surgery');
require('./pathology_report');
require('./biospecimen');
// require('./doc');
require('./bioexperiment');
require('./biofile');



module.exports = require('./app');
