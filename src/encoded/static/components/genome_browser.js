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
    let browserCfg;

    if (assembly === 'hg19') {
        if (region) {
            const reg = region.split(':');
            const chr = reg[0].substring(3, reg[0].length);
            let viewStart;
            let viewEnd;
            const positions = reg[1].split('-');
            for (let i = 0; i < positions.length; i += 1) {
                positions[i] = parseInt(positions[i].replace(/,/g, ''), 10);
            }
            if (positions.length > 1) {
                if (positions[0] > 10000) {
                    viewStart = positions[0] - 10000;
                } else {
                    viewStart = 1;
                }
                viewEnd = positions[1] + 10000;
            } else {
                if (positions[0] > 10000) {
                    viewStart = positions[0] - 10000;
                } else {
                    viewStart = 1;
                }
                viewEnd = positions[0] + 10000;
            }

            browserCfg = {
                chr: chr,
                viewStart: viewStart,
                viewEnd: viewEnd,
                sources: [
                    {
                        name: 'Genome',
                        twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/hg19.2bit',
                        tier_type: 'sequence',
                        provides_entrypoints: true,
                        pinned: true,
                    },
                    {
                        name: 'GENCODE',
                        bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.bb',
                        stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.xml',
                        collapseSuperGroups: true,
                        trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/geneIndex.ix',
                    },
                    {
                        name: 'Repeats',
                        desc: 'Repeat annotation from RepeatMasker',
                        bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/repeats.bb',
                        stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/bb-repeats.xml',
                        forceReduction: -1,
                    },
                ],
            };
        }
    } else if (assembly === 'mm10') {
        browserCfg = {
            chr: '19',
            viewStart: 30000000,
            viewEnd: 30100000,
            cookieKey: 'mouse38',
            coordSystem: { speciesName: 'Mouse', taxon: 10090, auth: 'GRCm', version: 38, ucscName: 'mm10' },
            sources: [
                {
                    name: 'Genome',
                    twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/mm10.2bit',
                    desc: 'Mouse reference genome build GRCm38',
                    tier_type: 'sequence',
                    provides_entrypoints: true,
                },
                {
                    name: 'Genes',
                    desc: 'Gene structures from GENCODE M2',
                    bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencodeM2.bb',
                    stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencode.xml',
                    collapseSuperGroups: true,
                    trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencodeM2.ix',
                },
                {
                    name: 'Repeats',
                    desc: 'Repeat annotation from UCSC',
                    bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/repeats.bb',
                    stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/bb-repeats2.xml',
                },
            ],
        };
    } else if (assembly === 'mm9') {
        browserCfg = {
            chr: '19',
            viewStart: 30000000,
            viewEnd: 30030000,
            cookieKey: 'mouse',
            coordSystem: { speciesName: 'Mouse', taxon: 10090, auth: 'NCBIM', version: 37 },
            sources: [
                {
                    name: 'Genome',
                    twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm9/mm9.2bit',
                    desc: 'Mouse reference genome build NCBIm37',
                    tier_type: 'sequence',
                    provides_entrypoints: true,
                },
            ],
        };
    } else if (assembly === 'dm3') {
        browserCfg = {
            chr: '3L',
            viewStart: 15940000,
            viewEnd: 15985000,
            cookieKey: 'drosophila',
            coordSystem: { speciesName: 'Drosophila', taxon: 7227, auth: 'BDGP', version: 5 },
            sources: [
                {
                    name: 'Genome',
                    twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/dm3/dm3.2bit',
                    desc: 'D. melanogaster reference genome build BDGP R5',
                    tier_type: 'sequence',
                    provides_entrypoints: true,
                },
            ],
        };
    }

    return browserCfg;
}


const GenomeBrowser = React.createClass({
    propTypes: {
        files: React.PropTypes.array.isRequired, // Array of files to represent
        assembly: React.PropTypes.string.isRequired, // Assembly to use with browser
        region: React.PropTypes.string, // Region to use with browser
        limitFiles: React.PropTypes.bool, // True to limit # files to maxFilesBrowsed
    },

    contextTypes: {
        location_href: React.PropTypes.string,
        localInstance: React.PropTypes.bool,
    },

    componentDidMount: function () {
        const { assembly, region, limitFiles } = this.props;
        console.log('ASSEMBLY: %s', assembly);

        // Extract only bigWig and bigBed files from the list:
        let files = this.props.files.filter(file => file.file_format === 'bigWig' || file.file_format === 'bigBed');

        // Make some fake file objects from "test" just to give the genome browser something to
        // chew on if we're running locally.
        files = !this.context.localInstance ?
            (limitFiles ? files.slice(0, maxFilesBrowsed - 1) : files)
        : dummyFiles;

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

        if (assembly === 'hg19') {
            if (this.props.region) {
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
            browserCfg.sources = [
                {
                    name: 'Genome',
                    twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/hg19.2bit',
                    tier_type: 'sequence',
                    provides_entrypoints: true,
                    pinned: true,
                },
                {
                    name: 'GENCODE',
                    bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.bb',
                    stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/gencode.xml',
                    collapseSuperGroups: true,
                    trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/geneIndex.ix',
                },
                {
                    name: 'Repeats',
                    desc: 'Repeat annotation from RepeatMasker',
                    bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/repeats.bb',
                    stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/hg19/bb-repeats.xml',
                    forceReduction: -1,
                },
            ];
        } else if (assembly === 'mm10') {
            browserCfg.chr = '19';
            browserCfg.viewStart = 30000000;
            browserCfg.viewEnd = 30100000;
            browserCfg.cookieKey = 'mouse38';
            browserCfg.coordSystem = { speciesName: 'Mouse', taxon: 10090, auth: 'GRCm', version: 38, ucscName: 'mm10' };
            browserCfg.sources = [
                {
                    name: 'Genome',
                    twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/mm10.2bit',
                    desc: 'Mouse reference genome build GRCm38',
                    tier_type: 'sequence',
                    provides_entrypoints: true,
                },
                {
                    name: 'Genes',
                    desc: 'Gene structures from GENCODE M2',
                    bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencodeM2.bb',
                    stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencode.xml',
                    collapseSuperGroups: true,
                    trixURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/gencodeM2.ix',
                },
                {
                    name: 'Repeats',
                    desc: 'Repeat annotation from UCSC',
                    bwgURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/repeats.bb',
                    stylesheet_uri: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm10/bb-repeats2.xml',
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

        this.browserFiles = []
        let domain = `${location.protocol}//${location.hostname}`;
        if (domain.includes('localhost')) {
            domain = domainName;
        }
        files.forEach((file) => {
            if (file.file_format === 'bigWig') {
                this.browserFiles.push({
                    name: file.accession,
                    desc: file.output_type,
                    bwgURI: `${domain}${file.href}`,
                    style: [
                        {
                            type: 'default',
                            style: {
                                glyph: 'HISTOGRAM',
                                HEIGHT: 30,
                                BGCOLOR: 'rgb(166,71,71)',
                            },
                        },
                    ],
                });
            } else if (file.file_format === 'bigBed') {
                this.browserFiles.push({
                    name: file.accession,
                    desc: file.output_type,
                    bwgURI: `${domain}${file.href}`,
                    style: [
                        {
                            style: {
                                HEIGHT: 10,
                            },
                        },
                    ],
                });
            }
        });
        if (this.browserFiles.length) {
            browserCfg.sources = browserCfg.sources.concat(this.browserFiles);
        }

        require.ensure(['dalliance'], (require) => {
            const Dalliance = require('dalliance').browser;

            this.browser = new Dalliance({
                maxHeight: 1000,
                noPersist: true,
                noPersistView: true,
                noTrackAdder: true,
                maxWorkers: 4,
                noHelp: true,
                chr: browserCfg.chr,
                viewStart: browserCfg.viewStart,
                viewEnd: browserCfg.viewEnd,
                cookieKey: browserCfg.cookieKey,
                coordSystem: browserCfg.coordSystem,
                sources: browserCfg.sources,
                noTitle: true,
                disablePoweredBy: true,
            });
        });
    },

    componentDidUpdate: function () {
        // Remove old tiers
        if (this.browser && this.browserFiles && this.browserFiles.length) {
            this.browserFiles.forEach((fileSource) => {
                this.browser.removeTier({
                    name: fileSource.name,
                    desc: fileSource.desc,
                    bwgURI: fileSource.bwgURI,
                });
            });
        }

        const files = !this.context.localInstance ? this.props.files.slice(0, maxFilesBrowsed - 1) : dummyFiles;
        if (files && files.length) {
            let domain = `${location.protocol}//${location.hostname}`;
            if (domain.includes('localhost')) {
                domain = domainName;
            }
            files.forEach((file) => {
                if (file.file_format === 'bigWig') {
                    this.browser.addTier({
                        name: file.accession,
                        desc: file.output_type,
                        bwgURI: `${domain}${file.href}`,
                        style: [
                            {
                                type: 'default',
                                style: {
                                    glyph: 'HISTOGRAM',
                                    HEIGHT: 30,
                                    BGCOLOR: 'rgb(166,71,71)',
                                },
                            },
                        ],
                    });
                } else if (file.file_format === 'bigBed') {
                    this.browser.addTier({
                        name: file.accession,
                        desc: file.output_type,
                        bwgURI: `${domain}${file.href}`,
                        style: [
                            {
                                style: {
                                    HEIGHT: 10,
                                },
                            },
                        ],
                    });
                }
            });
        }
    },

    render: function () {
        return (
            <div id="svgHolder" className="trackhub-element" />
        );
    },
});


export default GenomeBrowser;
