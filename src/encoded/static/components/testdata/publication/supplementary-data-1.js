module.exports = {
    "url": "http://encodenets.gersteinlab.org/metatracks/",
    "supplementary_data_type": "enhancer annotations",
    "data_summary": "Enhancers are identified as binding active regions (BARs) outside promoter-proximal regulatory modules (PRMs) and more than 10kb away from any GENCODE genes and non-coding genes. A random forest model trained on chromatin accessibility and histone modification has been used to identify BARs, using randomly sampled TF binding regions and non-binding regions as positive and negative training sets. PRMs are identified with a similar model as that for BARs, using TF binding regions at transcription start site (TSS) as positive training set, and non-binding regions or regions far away from TSS or both as negative training sets. This model has been applied to 5 ENCODE cell lines: GM12878, K562, h1-HESC, HeLa-S3, and Hep-G2.",
    "file_format": "BED",
    "identifiers": [
        "PMID:23000965"
    ]
};
