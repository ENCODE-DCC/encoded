import { filterAuditByPath } from '../audit';


describe('Audit module', () => {
    describe('Returns correct filtered audit object', () => {
        const audit = {
            INTERNAL_ACTION: [
                {
                    category: 'mismatched status',
                    detail: 'Released analysis {ENCAN307LTU|/analyses/ENCAN307LTU/} has in progress subobject quality standard {encode4-histone-chip|/quality-standards/encode4-histone-chip/}',
                    level: 30,
                    level_name: 'INTERNAL_ACTION',
                    path: '/analyses/ENCAN307LTU/',
                    name: 'audit_item_status',
                },
                {
                    category: 'mismatched status',
                    detail: 'Released experiment {ENCSR000AKP|/experiments/ENCSR000AKP/} has archived subobject analysis {ENCAN480VUK|/analyses/ENCAN480VUK/}',
                    level: 30,
                    level_name: 'INTERNAL_ACTION',
                    path: '/experiments/ENCSR000AKP/',
                    name: 'audit_item_status',
                },
            ],
            WARNING: [
                {
                    category: 'inconsistent platforms',
                    detail: 'possible_controls is a list of experiment(s) that can serve as analytical controls for a given experiment. Experiment {ENCSR000AKY|/experiments/ENCSR000AKY/} found in possible_controls list of this experiment contains data produced on platform(s) [Illumina HiSeq 2000/2500, Illumina Genome Analyzer II/e/x] which are not compatible with platform Illumina Genome Analyzer II/e/x used in this experiment.',
                    level: 40,
                    level_name: 'WARNING',
                    path: '/experiments/ENCSR000AKP/',
                    name: 'audit_experiment',
                },
                {
                    category: 'mild to moderate bottlenecking',
                    detail: 'PBC2 (PCR Bottlenecking Coefficient 2, M1/M2) is the ratio of the number of genomic locations where exactly one read maps uniquely (M1) to the number of genomic locations where two reads map uniquely (M2). A PBC2 value in the range 0 - 1 is severe bottlenecking, 1 - 3 is moderate bottlenecking, 3 - 10 is mild bottlenecking, > 10 is no bottlenecking. PBC2 value > 10 is recommended, but > 3 is acceptable.  ENCODE processed alignments file {ENCFF384ZZM|/files/ENCFF384ZZM/} was generated from a library with PBC2 value of 8.55.',
                    level: 40,
                    level_name: 'WARNING',
                    path: '/experiments/ENCSR000AKP/',
                    name: 'audit_experiment',
                },
            ],
            ERROR: [
                {
                    category: 'extremely low read depth',
                    detail: 'Processed alignments file {ENCFF907MNY|/files/ENCFF907MNY/} produced by Transcription factor ChIP-seq 2 pipeline ( {ENCPL367MAS|/pipelines/ENCPL367MAS/} ) using the GRCh38 assembly has 4917355 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H3K27ac-human and investigated as a narrow histone mark is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )',
                    level: 60,
                    level_name: 'ERROR',
                    path: '/analyses/ENCAN307LTU/',
                    name: 'audit_experiment',
                },
            ],
            NOT_COMPLIANT: [
                {
                    category: 'insufficient read depth',
                    detail: 'Processed alignments file {ENCFF301TVL|/files/ENCFF301TVL/} produced by ChIP-seq read mapping pipeline ( {ENCPL220NBH|/pipelines/ENCPL220NBH/} ) using the GRCh38 assembly has 9761907 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H3K27ac-human and investigated as a narrow histone mark is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )',
                    level: 50,
                    level_name: 'NOT_COMPLIANT',
                    path: '/experiments/ENCSR000AKP/',
                    name: 'audit_experiment',
                },
                {
                    category: 'insufficient read depth',
                    detail: 'Processed alignments file {ENCFF384ZZM|/files/ENCFF384ZZM/} produced by ChIP-seq read mapping pipeline ( {ENCPL220NBH|/pipelines/ENCPL220NBH/} ) using the hg19 assembly has 9770603 usable fragments. The minimum ENCODE standard for each replicate in a ChIP-seq experiment targeting H3K27ac-human and investigated as a narrow histone mark is 10 million usable fragments. The recommended value is > 20 million, but > 10 million is acceptable. (See {ENCODE ChIP-seq data standards|/data-standards/chip-seq/} )',
                    level: 50,
                    level_name: 'NOT_COMPLIANT',
                    path: '/analyses/ENCAN307LTU/',
                    name: 'audit_experiment',
                },
            ],
        };

        it('Returns larger filtered result with /experiments/ENCSR000AKP/', () => {
            const filteredAudit = filterAuditByPath(audit, '/experiments/ENCSR000AKP/');

            expect(filteredAudit).toHaveProperty('INTERNAL_ACTION');
            expect(filteredAudit).toHaveProperty('WARNING');
            expect(filteredAudit).not.toHaveProperty('ERROR');
            expect(filteredAudit).toHaveProperty('NOT_COMPLIANT');

            expect(filteredAudit.INTERNAL_ACTION).toHaveLength(1);
            expect(filteredAudit.WARNING).toHaveLength(2);
            expect(filteredAudit.NOT_COMPLIANT).toHaveLength(1);

            expect(filteredAudit.INTERNAL_ACTION[0].path).toEqual('/experiments/ENCSR000AKP/');
            expect(filteredAudit.WARNING[0].path).toEqual('/experiments/ENCSR000AKP/');
            expect(filteredAudit.WARNING[1].path).toEqual('/experiments/ENCSR000AKP/');
            expect(filteredAudit.NOT_COMPLIANT[0].path).toEqual('/experiments/ENCSR000AKP/');
        });

        it('Returns smaller filtered result with /analyses/ENCAN307LTU/', () => {
            const filteredAudit = filterAuditByPath(audit, '/analyses/ENCAN307LTU/');

            expect(filteredAudit).toHaveProperty('INTERNAL_ACTION');
            expect(filteredAudit).not.toHaveProperty('WARNING');
            expect(filteredAudit).toHaveProperty('ERROR');
            expect(filteredAudit).toHaveProperty('NOT_COMPLIANT');

            expect(filteredAudit.INTERNAL_ACTION).toHaveLength(1);
            expect(filteredAudit.ERROR).toHaveLength(1);
            expect(filteredAudit.NOT_COMPLIANT).toHaveLength(1);

            expect(filteredAudit.INTERNAL_ACTION[0].path).toEqual('/analyses/ENCAN307LTU/');
            expect(filteredAudit.ERROR[0].path).toEqual('/analyses/ENCAN307LTU/');
            expect(filteredAudit.NOT_COMPLIANT[0].path).toEqual('/analyses/ENCAN307LTU/');
        });

        it('Returns empty object when given an empty audit', () => {
            const filteredAudit = filterAuditByPath({}, '/analyses/ENCAN307LTU/');

            expect(Object.keys(filteredAudit)).toHaveLength(0);
        });
    });
});
