module.exports = {
    '@context': '/terms/',
    '@graph': [
        {
            '@id': '/experiments/ENCSR808QCJ/',
            '@type': [
                'Experiment',
                'Dataset',
                'Item',
            ],
            accession: 'ENCSR808QCJ',
            assay_term_name: 'ATAC-seq',
            assay_title: 'ATAC-seq',
            award: { project: 'ENCODE' },
            biosample_ontology: { term_name: 'GM12878' },
            biosample_summary: 'GM12878',
            files: [
                { '@id': '/files/ENCFF164JWT/' },
                { '@id': '/files/ENCFF032OJW/' },
                { '@id': '/files/ENCFF182CHA/' },
            ],
            lab: { title: 'Michael Snyder, Stanford' },
            replicates: [
                {
                    library: {
                        biosample: {
                            age_units: 'year',
                            life_stage: 'adult',
                            accession: 'ENCBS630AAA',
                            organism: { scientific_name: 'Homo sapiens' },
                            age: '53',
                        },
                    },
                    biological_replicate_number: 1,
                    technical_replicate_number: 1,
                    '@id': '/replicates/0311d1e6-a141-4be4-a165-6abc6d320f05/',
                },
            ],
            status: 'released',
        },
        {
            '@id': '/experiments/ENCSR751YPU/',
            '@type': [
                'Experiment',
                'Dataset',
                'Item',
            ],
            accession: 'ENCSR751YPU',
            assay_term_name: 'DNase-seq',
            assay_title: 'DNase-seq',
            award: { project: 'Roadmap' },
            biosample_ontology: { term_name: 'midbrain' },
            biosample_summary: 'midbrain male adult (34 years)',
            files: [
                { '@id': '/files/ENCFF477MLC/' },
                { '@id': '/files/ENCFF000LBC/' },
                { '@id': '/files/ENCFF000LBB/' },
                { '@id': '/files/ENCFF000LBA/' },
                { '@id': '/files/ENCFF000LAZ/' },
                { '@id': '/files/ENCFF010LAO/' },
            ],
            lab: { title: 'John Stamatoyannopoulos, UW' },
            replicates: [
                {
                    library: {
                        biosample: {
                            age_units: 'year',
                            life_stage: 'adult',
                            accession: 'ENCBS804RUL',
                            organism: { scientific_name: 'Homo sapiens' },
                            age: '34',
                        },
                    },
                    biological_replicate_number: 1,
                    technical_replicate_number: 1,
                    '@id': '/replicates/952fc6c6-f155-47e8-ab0f-d44d48880d11/',
                },
            ],
            status: 'released',
        },
    ],
    '@id': '/search/?type=Experiment&status=released&assay_slims=DNA+accessibility&format=json',
    '@type': ['Search'],
    clear_filters: '/search/?type=Experiment',
    facets: [
        {
            terms: [
                {
                    doc_count: 2,
                    key: 'Dataset',
                },
                {
                    doc_count: 2,
                    key: 'Experiment',
                },
            ],
            type: 'terms',
            field: 'type',
            total: 2,
            title: 'Data Type',
            appended: false,
        },
        {
            terms: [
                {
                    doc_count: 18,
                    key: 'DNA binding',
                },
                {
                    doc_count: 12,
                    key: 'Transcription',
                },
            ],
            type: 'terms',
            field: 'assay_slims',
            total: 46,
            title: 'Assay type',
            appended: false,
        },
        {
            terms: [
                {
                    doc_count: 2,
                    key: 'fastq',
                },
                {
                    doc_count: 1,
                    key: 'bam',
                },
                {
                    doc_count: 1,
                    key: 'bed narrowPeak',
                },
                {
                    doc_count: 1,
                    key: 'csfasta',
                },
                {
                    doc_count: 1,
                    key: 'csqual',
                },
            ],
            type: 'terms',
            field: 'files.file_type',
            total: 2,
            title: 'Available file types',
            appended: false,
        },
        {
            terms: [
                {
                    doc_count: 1,
                    key: 'GRCh38',
                },
            ],
            type: 'terms',
            field: 'assembly',
            total: 2,
            title: 'Genome assembly',
            appended: false,
        },
    ],
    filters: [
        {
            field: 'status',
            remove: '/search/?type=Experiment&assay_slims=DNA+accessibility&format=json',
            term: 'released',
        },
        {
            field: 'assay_slims',
            remove: '/search/?type=Experiment&status=released&format=json',
            term: 'DNA accessibility',
        },
        {
            field: 'type',
            remove: '/search/?status=released&assay_slims=DNA+accessibility&format=json',
            term: 'Experiment',
        },
    ],
    notification: 'Success',
    sort: {
        date_created: {
            order: 'desc',
            unmapped_type: 'keyword',
        },
        label: {
            order: 'desc',
            unmapped_type: 'keyword',
        },
        uuid: {
            order: 'desc',
            unmapped_type: 'keyword',
        },
    },
    title: 'Search',
    total: 2,
};
