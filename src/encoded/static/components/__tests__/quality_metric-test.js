import { isRenderableProp } from '../quality_metric';
import chipseqFilterQCSchema from '../../../schemas/chipseq_filter_quality_metric.json';

describe('Quality Metric Module', () => {
    const chipseqFilterQC = {
        cross_correlation_plot: {
            href: '@@download/cross_correlation_plot/ENCFF002DSJ.raw.srt.filt.nodup.srt.filt.nodup.sample.15.SE.tagAlign.gz.cc.plot.pdf',
            md5sum: '9dd6e464eb48a2f36edd1de029752081',
            type: 'application/pdf',
            download: 'ENCFF002DSJ.raw.srt.filt.nodup.srt.filt.nodup.sample.15.SE.tagAlign.gz.cc.plot.pdf',
        },
        NRF: 0.926866,
        NSC: 1.02,
        'fragment length': 180,
        PBC1: 0.94,
        PBC2: 0.94,
        RSC: 0.98,
    };

    it('Properly detects renderable QC properties', () => {
        const expectedResults = {
            cross_correlation_plot: false,
            NRF: true,
            NSC: true,
            'fragment length': true,
            PBC1: true,
            PBC2: true,
            RSC: true,
        };

        Object.keys(chipseqFilterQC).forEach((key) => {
            expect(isRenderableProp(key, chipseqFilterQC, chipseqFilterQCSchema)).toEqual(expectedResults[key]);
        });
    });
});
