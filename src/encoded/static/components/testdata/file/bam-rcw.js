module.exports = {
    "@id": "/files/ENCFF001RCW/",
    "@type": ["File", "Item"],
    "accession": "ENCFF001RCW",
    "award": "ENCODE2",
    "dataset": require('../experiment')['@id'],
    "derived_from": [require('./bam-vuq')['@id'], require('./bam-vus')['@id']],
    "file_format": "bam",
    "file_size": 2433593,
    "lab": "j-michael-cherry",
    "md5sum": "ecff397bffc54f01319eb41c6194379b",
    "output_type": "alignments",
    "status": "released",
    "analysis_step": require('../analysis_step/encode-2-step'),
    "submitted_by": "platea.a@volutpat.viverra",
    "submitted_file_name": "replicate2.bam",
    "uuid": "895fef10-52ed-11e4-916c-0800200c9a66"
};
