module.exports = {
    "@id": "/files/ENCFF005COS/",
    "@type": ["File", "Item"],
    "accession": "ENCFF005COS",
    "assembly": "hg19",
    "award": "ENCODE2",
    "dataset": require('../experiment')['@id'],
    "derived_from": [require('./bam-vuq')['@id']],
    "file_format": "bed_narrowPeak",
    "file_size": 2433593,
    "lab": "j-michael-cherry",
    "md5sum": "9e39f46aa18273f269360535fce32ed2",
    "output_type": "UniformlyProcessedPeakCalls",
    "status": "released",
    "analysis_step_version": require('../analysis_step/step-version-1'), // @calculated_property
    "step_run": require('../analysis_step/step-run-1'),
    "submitted_by": "amet.fusce@est.fermentum",
    "submitted_file_name": "../../wgEncodeAwg/wgEncodeAwgTfbsSydhGm12878Ebf1sc137065UniPk.narrowPeak",
    "biological_replicates": [ ],
    "uuid": "956cba28-ccff-4cbd-b1c8-39db4e3de572"
};
