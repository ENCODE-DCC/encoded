import _ from 'underscore';


// Import test component and data.
import { compileAnalyses } from '../filegallery';


const experiment0 = {
    analysis_objects: [
        {
            files: [
                '/files/ENCFF003MRN/',
                '/files/ENCFF005MRN/',
            ],
            assembly: 'GRCh38',
            genome_annotation: 'V24',
            pipelines: [
                '/pipelines/ENCPL001MRN/',
                '/pipelines/ENCPL003RNA/',
            ],
            pipeline_award_rfas: [
                'ENCODE3',
            ],
            pipeline_labs: [
                '/labs/brenton-graveley/',
                '/labs/thomas-gingeras/',
            ],
        },
        {
            files: [
                '/files/ENCFF004MRN/',
                '/files/ENCFF006MRN/',
                '/files/ENCFF807TRA/',
                '/files/ENCFF783YZT/',
            ],
            assembly: 'hg19',
            pipelines: [
                '/pipelines/ENCPL001MRN/',
                '/pipelines/ENCPL003RNA/',
            ],
            pipeline_award_rfas: [
                'ENCODE4',
            ],
            pipeline_labs: [
                '/labs/encode-processing-pipeline/',
            ],
        },
        {
            files: [
                '/files/ENCFF001RCY/',
                '/files/ENCFF001RCV/',
            ],
            assembly: 'GRCh38',
            pipelines: [
                '/pipelines/ENCPL001GRV/',
            ],
            pipeline_award_rfas: [
                'ENCODE3',
            ],
            pipeline_labs: [
                '/labs/encode-processing-pipeline/',
            ],
        },
        {
            files: [
                '/files/ENCFF807TRA/',
                '/files/ENCFF783YZT/',
            ],
            assembly: 'GRCh38',
            pipelines: [
                '/pipelines/ENCPL001GRV/',
            ],
            pipeline_award_rfas: [
                'ENCODE3',
            ],
            pipeline_labs: [
                '/labs/encode-processing-pipeline/',
            ],
        },
        {
            files: [
                '/files/ENCFF001RCZ/',
                '/files/ENCFF001RCW/',
            ],
            assembly: 'GRCh38',
            genome_annotation: 'V24',
            pipelines: [
                '/pipelines/ENCPL001GRV/',
            ],
            pipeline_award_rfas: [
                'ENCODE4',
            ],
            pipeline_labs: [
                '/labs/encode-processing-pipeline/',
            ],
        },
    ],
};

const files0 = [
    {
        '@id': '/files/ENCFF003MRN/',
        accession: 'ENCFF003MRN',
        assembly: 'GRCh38',
        dataset: 'ENCSR123MRN',
        file_format: 'bam',
        genome_annotation: 'V24',
        lab: '/labs/encode-processing-pipeline/',
        output_type: 'alignments',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF005MRN/',
        accession: 'ENCFF005MRN',
        assembly: 'GRCh38',
        dataset: 'ENCSR123MRN',
        file_format: 'tsv',
        genome_annotation: 'V24',
        lab: '/labs/encode-processing-pipeline/',
        output_type: 'transcript quantifications',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF004MRN/',
        accession: 'ENCFF004MRN',
        assembly: 'GRCh38',
        dataset: 'ENCSR123MRN',
        file_format: 'bam',
        genome_annotation: 'V24',
        lab: '/labs/encode-processing-pipeline/',
        output_type: 'alignments',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF006MRN/',
        accession: 'ENCFF006MRN',
        assembly: 'GRCh38',
        dataset: 'ENCSR123MRN',
        file_format: 'tsv',
        genome_annotation: 'V24',
        lab: '/labs/encode-processing-pipeline/',
        output_type: 'transcript quantifications',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF807TRA/',
        accession: 'ENCFF807TRA',
        dataset: 'ENCSR123MRN',
        file_format: 'gtf',
        assembly: 'hg19',
        lab: '/labs/encode-processing-pipeline/',
        output_type: 'transcriptome annotations',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF783YZT/',
        accession: 'ENCFF783YZT',
        dataset: 'ENCSR123MRN',
        file_format: 'gff',
        file_format_type: 'gff3',
        assembly: 'hg19',
        lab: '/labs/encode-processing-pipeline/',
        output_type: 'miRNA annotations',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF001RCZ/',
        accession: 'ENCFF001RCZ',
        dataset: 'ENCSR000AEN',
        file_format: 'bigWig',
        lab: '/labs/j-michael-cherry/',
        assembly: 'hg19',
        genome_annotation: 'V19',
        output_type: 'signal of all reads',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF001RCW/',
        accession: 'ENCFF001RCW',
        dataset: 'ENCSR000AEN',
        assembly: 'hg19',
        genome_annotation: 'V19',
        file_format: 'bam',
        lab: '/labs/j-michael-cherry/',
        output_type: 'alignments',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF001RCY/',
        accession: 'ENCFF001RCY',
        dataset: 'ENCSR000AEN',
        file_format: 'bigWig',
        assembly: 'GRCh38',
        genome_annotation: 'V19',
        lab: '/labs/j-michael-cherry/',
        output_type: 'signal of all reads',
        status: 'released',
    },
    {
        '@id': '/files/ENCFF001RCV/',
        accession: 'ENCFF001RCV',
        award: 'U41HG006992',
        dataset: 'ENCSR000AEN',
        assembly: 'hg19',
        genome_annotation: 'V19',
        file_format: 'bam',
        lab: '/labs/j-michael-cherry/',
        output_type: 'alignments',
        status: 'released',
    },
];


describe('createPipelineFacetObject', () => {
    describe('Both processed', () => {
        it('Has both ENCODE Uniform and Lab Custom facet terms and count', () => {
            const analysisObjects = compileAnalyses(experiment0, files0);
            expect(analysisObjects).toHaveLength(4);
            expect(analysisObjects[0].pipelineLab).toEqual('Mixed');
            expect(analysisObjects[0].assembly).toEqual('GRCh38 V24');
            expect(analysisObjects[0].files).toHaveLength(2);
            expect(analysisObjects[1].pipelineLab).toEqual('ENCODE4 uniform');
            expect(analysisObjects[1].assembly).toEqual('GRCh38 V24');
            expect(analysisObjects[1].files).toHaveLength(2);
            expect(analysisObjects[2].pipelineLab).toEqual('ENCODE3 uniform');
            expect(analysisObjects[2].assembly).toEqual('GRCh38');
            expect(analysisObjects[2].files).toHaveLength(4);
            expect(analysisObjects[3].pipelineLab).toEqual('ENCODE4 uniform');
            expect(analysisObjects[3].assembly).toEqual('hg19');
            expect(analysisObjects[3].files).toHaveLength(4);
        });
    });
});
