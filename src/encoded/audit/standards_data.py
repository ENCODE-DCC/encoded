
broad_peaks_targets = [
    'H3K36me3-human',
    'H3K36me3-mouse',

    'H3K4me1-human',
    'H3K4me1-mouse',

    'H3K79me2-human',
    'H3K79me2-mouse',

    'H3K27me3-human',
    'H3K27me3-mouse',

    'H3K9me1-human',
    'H3K9me1-mouse',

    'H3K9me3-human',  # exception
    'H3K9me3-mouse',  # exception

    'H3K9me2-human',
    'H3K9me2-mouse',

    'H3F3A-human',
    'H3F3A-mouse',

    'H4K20me1-human',
    'H4K20me1-mouse',

    'H3K79me3-human',
    'H3K79me3-mouse',
    ]

pipelines_with_read_depth = {
    'Small RNA-seq single-end pipeline': 30000000,
    'RNA-seq of long RNAs (paired-end, stranded)': 30000000,
    'RNA-seq of long RNAs (single-end, unstranded)': 30000000,
    'RAMPAGE (paired-end, stranded)': 20000000,
    'ChIP-seq read mapping': {
        'narrow': 20000000,
        'broad': 45000000
    },
    'Transcription factor ChIP-seq pipeline (modERN)': 3000000
    }


special_assays_with_read_depth = {
    'shRNA knockdown followed by RNA-seq': 10000000,
    'siRNA knockdown followed by RNA-seq': 10000000,
    'CRISPRi followed by RNA-seq': 10000000,
    'CRISPR genome editing followed by RNA-seq': 10000000,
    'single cell isolation followed by RNA-seq': 5000000
    }


minimal_read_depth_requirements = {
    'ChIP-seq': 20000000,
    'RAMPAGE': 10000000,
    'shRNA knockdown followed by RNA-seq': 10000000,
    'siRNA knockdown followed by RNA-seq': 10000000,
    'single cell isolation followed by RNA-seq': 10000000,
    'CRISPR genome editing followed by RNA-seq': 10000000,
    'modENCODE-chip': 500000
}
