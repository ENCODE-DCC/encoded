import React from 'react';
import url from 'url';


const GenomeBrowser = React.createClass({
    propTypes: {
        files: React.PropTypes.array.isRequired, // Array of files to represent
        assembly: React.PropTypes.array.isRequired, // Assembly to use with browser
        region: React.PropTypes.string, // Region to use with browser
    },

    contextTypes: {
        location_href: React.PropTypes.string,
    },

    componentDidMount: function () {
        require.ensure(['dalliance'], (require) => {
            const Dalliance = require('dalliance').browser;

            // Get the current domain name.
            const urlInfo = url.parse(this.context.location_href);
            const domainName = `${urlInfo.protocol}//${urlInfo.host}`;

            const browser = new Dalliance({
                maxHeight: 1000,
                noPersist: true,
                noPersistView: true,
                noTrackAdder: true,
                maxWorkers: 4,
                noHelp: true,
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
                noTitle: true,
                disablePoweredBy: true,
            });
            const { files, assembly, region } = this.props;
            browser.sources = [];
            if (assembly[0] === 'hg19') {
                if (this.props.region) {
                    const reg = region.split(':');
                    browser.chr = reg[0].substring(3, reg[0].length);
                    const positions = reg[1].split('-');
                    for (let i = 0; i < positions.length; i += 1) {
                        positions[i] = parseInt(positions[i].replace(/,/g, ''), 10);
                    }
                    if (positions.length > 1) {
                        if (positions[0] > 10000) {
                            browser.viewStart = positions[0] - 10000;
                        } else {
                            browser.viewStart = 1;
                        }
                        browser.viewEnd = positions[1] + 10000;
                    } else {
                        if (positions[0] > 10000) {
                            browser.viewStart = positions[0] - 10000;
                        } else {
                            browser.viewStart = 1;
                        }
                        browser.viewEnd = positions[0] + 10000;
                    }
                }
                browser.sources = [
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
            } else if (assembly[0] === 'mm10') {
                browser.chr = '19';
                browser.viewStart = 30000000;
                browser.viewEnd = 30100000;
                browser.cookieKey = 'mouse38';
                browser.coordSystem = { speciesName: 'Mouse', taxon: 10090, auth: 'GRCm', version: 38, ucscName: 'mm10' };
                browser.sources = [
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
            } else if (assembly[0] === 'mm9') {
                browser.chr = '19';
                browser.viewStart = 30000000;
                browser.viewEnd = 30030000;
                browser.cookieKey = 'mouse';
                browser.coordSystem = { speciesName: 'Mouse', taxon: 10090, auth: 'NCBIM', version: 37 };
                browser.sources = [
                    {
                        name: 'Genome',
                        twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/mm9/mm9.2bit',
                        desc: 'Mouse reference genome build NCBIm37',
                        tier_type: 'sequence',
                        provides_entrypoints: true,
                    },
                ];
            } else if (assembly[0] === 'dm3') {
                browser.chr = '3L';
                browser.viewStart = 15940000;
                browser.viewEnd = 15985000;
                browser.cookieKey = 'drosophila';
                browser.coordSystem = { speciesName: 'Drosophila', taxon: 7227, auth: 'BDGP', version: 5 };
                browser.sources = [
                    {
                        name: 'Genome',
                        twoBitURI: 'https://s3-us-west-1.amazonaws.com/encoded-build/browser/dm3/dm3.2bit',
                        desc: 'D. melanogaster reference genome build BDGP R5',
                        tier_type: 'sequence',
                        provides_entrypoints: true,
                    },
                ];
            }
            files.forEach((file) => {
                if (file.file_format === 'bigWig') {
                    browser.sources.push({
                        name: file.output_type,
                        desc: file.accession,
                        bwgURI: `${domainName}${file.href}`,
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
                    browser.sources.push({
                        name: file.output_type,
                        desc: file.accession,
                        bwgURI: `${domainName}${file.href}`,
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
        });
    },

    render: function () {
        return (
            <div id="svgHolder" className="trackhub-element" />
        );
    },
});


export default GenomeBrowser;
