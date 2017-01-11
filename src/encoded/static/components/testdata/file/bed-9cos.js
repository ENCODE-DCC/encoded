module.exports = {
    "@id": "/files/ENCFF008COS/",
    "@type": ["File", "Item"],
    "accession": "ENCFF008COS",
    "award": "ENCODE2",
    "dataset": require('../experiment')['@id'],
    "derived_from": [require('./bam-vuq')['@id'], require('./bam-vus')['@id']],
    "file_format": "bed_narrowPeak",
    "file_size": 2433593,
    "lab": "j-michael-cherry",
    "md5sum": "9e39f46aa18273f269360535fce32ed2",
    "output_type": "UniformlyProcessedPeakCalls",
    "status": "released",
    "analysis_step": require('../analysis_step/encode-2-step'),
    "submitted_by": "amet.fusce@est.fermentum",
    "submitted_file_name": "../../wgEncodeAwg/wgEncodeAwgTfbsSydhGm12878Ebf1sc137065UniPk.narrowPeak",
    "uuid": "956cba28-ccff-4cbd-b1c8-39db4e3de572"
};
