import React from 'react';


const maxFilesBrowsed = 5; // Maximum number of files to browse
const domainName = 'https://www.encodeproject.org';
const dummyFiles = [
    {
        file_format: 'bigWig',
        output_type: 'minus strand signal of all reads',
        accession: 'ENCFF425LKJ',
        href: '/files/ENCFF425LKJ/@@download/ENCFF425LKJ.bigWig',
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of all reads',
        accession: 'ENCFF638QHN',
        href: '/files/ENCFF638QHN/@@download/ENCFF638QHN.bigWig',
    },
    {
        file_format: 'bigWig',
        output_type: 'plus strand signal of unique reads',
        accession: 'ENCFF541XFO',
        href: '/files/ENCFF541XFO/@@download/ENCFF541XFO.bigWig',
    },
    {
        file_format: 'bigBed',
        output_type: 'transcription start sites',
        accession: 'ENCFF517WSY',
        href: '/files/ENCFF517WSY/@@download/ENCFF517WSY.bigBed',
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF026DAN',
        href: '/files/ENCFF026DAN/@@download/ENCFF026DAN.bigBed',
    },
    {
        file_format: 'bigBed',
        output_type: 'peaks',
        accession: 'ENCFF847CBY',
        href: '/files/ENCFF847CBY/@@download/ENCFF847CBY.bigBed',
    },
];


function rAssemblyToSources(assembly, region) {
    const browserCfg = {
        chr: '22',
        viewStart: 29890000,
        viewEnd: 30050000,
        cookieKey: 'human-grc_h37-fp',
        coordSystem: {
            speciesName: 'Human',
            taxon: 9606,
            auth: 'GRCh',
            version: '37',
            ucscName: 'hg19',
        },
        sources: [],
    };

    if (assembly === 'GRCh38' || assembly === 'hg19') {
        // Hopefully region will work for both GRCh38 and hg19
        if (region) {
            const reg = region.split(':');
            browserCfg.chr = reg[0].substring(3, reg[0].length);
            const positions = reg[1].split('-');
            for (let i = 0; i < positions.length; i += 1) {
                positions[i] = parseInt(positions[i].replace(/,/g, ''), 10);
            }
            if (positions.length > 1) {
                if (positions[0] > 10000) {
                    browserCfg.viewStart = positions[0] - 10000;
                } else {
                    browserCfg.viewStart = 1;
                }
                browserCfg.viewEnd = positions[1] + 10000;
            } else {
                if (positions[0] > 10000) {
                    browserCfg.viewStart = positions[0] - 10000;
                } else {
                    browserCfg.viewStart = 1;
                }
                browserCfg.viewEnd = positions[0] + 10000;
            }
        }
    }

    if (assembly === 'GRCh38') {
        // sources:
        // Genome: faToTwoBit GRCh38_no_alt_analysis_set_GCA_000001405.15.fa.gz
        // gencode: http://ngs.sanger.ac.uk/production/gencode/trackhub/data/gencode.v24.annotation.bb
        // repeats: http://www.biodalliance.org/datasets/GRCh38/repeats.bb
        browserCfg.sources = [
            {
                name: 'Genome',
                desc: 'Human reference genome build GRCh38/hg38 (GRCh38_no_alt_analysis_set_GCA_000001405.15)',
                twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/GRCh38/GRCh38_no_alt_analysis_set_GCA_000001405.15.2bit',
                tier_type: 'sequence',
                provides_entrypoints: true,
                pinned: true,
            },
            {
                name: 'GENCODE',
                desc: 'Gene structures from GENCODE v24',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/GRCh38/gencode.v24.annotation.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/GRCh38/gencode2_v24.xml',
                collapseSuperGroups: true,
                trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/GRCh38/gencode.v24.annotation.ix',
            },
            {
                name: 'Repeats',
                desc: 'Repeat annotation from RepeatMasker',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/GRCh38/repeats_GRCh38.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/GRCh38/bb-repeats2_GRCh38.xml',
                forceReduction: -1,
            },
        ];
    } else if (assembly === 'hg19') {
        // sources:
        // Genome: faToTwoBit male.hg19.fa.gz
        // gencode: http://ngs.sanger.ac.uk/production/gencode/trackhub/data/gencode.v19.annotation.bb
        // repeats: http://www.biodalliance.org/datasets/GRCh38/repeats.bb
        browserCfg.sources = [
            {
                name: 'Genome',
                desc: 'Human reference genome build GRCh37/hg19',
                twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/male.hg19.2bit',
                tier_type: 'sequence',
                provides_entrypoints: true,
                pinned: true,
            },
            {
                name: 'GENCODE',
                desc: 'Gene structures from GENCODE v19',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.v19.annotation.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode_v19.xml',
                collapseSuperGroups: true,
                trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.v19.annotation.ix',
            },
            {
                name: 'Repeats',
                desc: 'Repeat annotation from RepeatMasker',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/repeats_hg19.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/bb-repeats_hg19.xml',
                forceReduction: -1,
            },
        ];
    } else if (assembly === 'mm10') {
        browserCfg.chr = '19';
        browserCfg.viewStart = 30000000;
        browserCfg.viewEnd = 30100000;
        browserCfg.cookieKey = 'mouse38';
        browserCfg.coordSystem = { speciesName: 'Mouse', taxon: 10090, auth: 'GRCm', version: 38, ucscName: 'mm10' };
        // sources:
        // Genome: faToTwoBit mm10_no_alt_analysis_set_ENCODE.fa.gz
        // gencode: http://ngs.sanger.ac.uk/production/gencode/trackhub/data/gencode.vMm.annotation.bb
        // repeats: http://www.biodalliance.org/datasets/GRCm38/repeats.bb
        browserCfg.sources = [
            {
                name: 'Genome',
                twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/mm10_no_alt_analysis_set_ENCODE.2bit',
                desc: 'Mouse reference genome build GRCm38',
                tier_type: 'sequence',
                provides_entrypoints: true,
            },
            {
                name: 'Genes',
                desc: 'Gene structures from GENCODE M2',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencode.vM4.annotation.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencode_vM4.xml',
                collapseSuperGroups: true,
                trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencode.vM4.annotation.ix',
            },
            {
                name: 'Repeats',
                desc: 'Repeat annotation from UCSC',
                bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/repeats_mm10.bb',
                stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/bb-repeats2_mm10.xml',
            },
        ];
    } else if (assembly === 'mm9') {
        browserCfg.chr = '19';
        browserCfg.viewStart = 30000000;
        browserCfg.viewEnd = 30030000;
        browserCfg.cookieKey = 'mouse';
        browserCfg.coordSystem = { speciesName: 'Mouse', taxon: 10090, auth: 'NCBIM', version: 37 };
        browserCfg.sources = [
            {
                name: 'Genome',
                twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm9/mm9.2bit',
                desc: 'Mouse reference genome build NCBIm37',
                tier_type: 'sequence',
                provides_entrypoints: true,
            },
        ];
    } else if (assembly === 'dm3') {
        browserCfg.chr = '3L';
        browserCfg.viewStart = 15940000;
        browserCfg.viewEnd = 15985000;
        browserCfg.cookieKey = 'drosophila';
        browserCfg.coordSystem = { speciesName: 'Drosophila', taxon: 7227, auth: 'BDGP', version: 5 };
        browserCfg.sources = [
            {
                name: 'Genome',
                twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/dm3/dm3.2bit',
                desc: 'D. melanogaster reference genome build BDGP R5',
                tier_type: 'sequence',
                provides_entrypoints: true,
            },
        ];
    }

    return browserCfg;
}


const GenomeBrowser = React.createClass({
    propTypes: {
        files: React.PropTypes.array.isRequired, // Array of files to represent
        assembly: React.PropTypes.string.isRequired, // Assembly to use with browser
        region: React.PropTypes.string, // Region to use with browser
        visBlobs: React.PropTypes.object, // This should contain one or more vis_blobs for dataset(s)
        limitFiles: React.PropTypes.bool, // True to limit # files to maxFilesBrowsed
    },

    contextTypes: {
        location_href: React.PropTypes.string,
        localInstance: React.PropTypes.bool,
    },

    componentDidMount: function () {
        require.ensure(['tnt.genome'], (require) => {
            require('d3');
            const TntGenomeBoard = require('tnt.genome');
            const genome = TntGenomeBoard.genome().species("human").gene("brca2").width(818);
            const geneTrack = TntGenomeBoard.track()
                .height(200)
                .color('white')
                .display(TntGenomeBoard.track.feature.genome.gene().color('#550055'))
                .data(TntGenomeBoard.track.data.genome.gene());
            const sequenceTrack = TntGenomeBoard.track()
                .height(30)
                .color('white')
                .display(TntGenomeBoard.track.feature.genome.sequence())
                .data(TntGenomeBoard.track.data.genome.sequence().limit(150));
            genome.zoom_in(100)
                .add_track(sequenceTrack)
                .add_track(geneTrack);
            genome(document.getElementById('svgHolder'));
            genome.start();
        });
    },

    componentDidUpdate: function () {
    },

    makeTrackLabel: function (file) {
        const datasetAccession = file.dataset.split('/')[2];
        // TODO: unreleased files are not in visBlob so get default labels
        const trackLabels = {
            shortLabel: file.accession,
            longLabel: `${file.status} ${file.output_type}`,
        };
        if (this.props.visBlobs === undefined || this.props.visBlobs === null) {
            return trackLabels;
        }
        Object.keys(this.props.visBlobs).forEach((blobKey) => {
            if (blobKey.startsWith(datasetAccession)) {
                const tracks = this.props.visBlobs[blobKey].tracks;
                const trackCount = tracks.length;
                for (let ix = 0; ix < trackCount; ix += 1) {
                    if (tracks[ix].name === file.accession) {
                        trackLabels.shortLabel = tracks[ix].shortLabel;
                        trackLabels.longLabel = tracks[ix].longLabel;
                        break;
                    }
                }
            }
        });
        return trackLabels;
    },

    render: function () {
        return (
            <div id="svgHolder" className="trackhub-element" />
        );
    },
});


export default GenomeBrowser;
