'use strict'
var React = require('react');
var $script = require('scriptjs');

module.exports.GenomeBrowser = React.createClass({
    componentDidMount: function () {
        $script('dalliance', function() {
            var Dalliance = require('dalliance').browser;
            var browser = new Dalliance({
                chr:          '22',
                viewStart:    29890000,
                viewEnd:      30050000,
                cookieKey:    'human-grc_h37-fp',
                coordSystem: {
                    speciesName: 'Human',
                    taxon: 9606,
                    auth: 'GRCh',
                    version: '37',
                    ucscName: 'hg19',
                },
                sources: [],
                noTitle: true,
                disablePoweredBy: true
            });
            var files = this.props.files;
            browser.sources = [];
            var assembly = this.props.assembly;
            if(assembly[0] == 'hg19') {
                browser.sources = [
                    {
                        name: 'Genome',
                        twoBitURI: 'https://www.biodalliance.org/datasets/hg19.2bit',
                        tier_type: 'sequence',
                        provides_entrypoints: true,
                        pinned: true
                    },
                    {
                        name: 'GENCODE',
                        bwgURI: 'https://www.biodalliance.org/datasets/gencode.bb',
                        stylesheet_uri: 'http://www.biodalliance.org/stylesheets/gencode.xml',
                        collapseSuperGroups: true,
                        trixURI: 'https://www.biodalliance.org/datasets/geneIndex.ix'
                    },
                    {
                        name: 'Repeats',
                        desc: 'Repeat annotation from RepeatMasker',
                        bwgURI: 'https://www.biodalliance.org/datasets/repeats.bb',
                        stylesheet_uri: 'https://www.biodalliance.org/stylesheets/bb-repeats.xml',
                        forceReduction: -1
                    }
                ];
            }
            else if(assembly[0] == 'mm10') {
                browser.chr = '19';
                browser.viewStart = 30000000;
                browser.viewEnd = 30100000;
                browser.cookieKey = 'mouse38';
                browser.coordSystem = {speciesName: 'Mouse', taxon: 10090, auth: 'GRCm', version: 38, ucscName: 'mm10'};
                browser.sources = [
                    {
                        name: 'Genome',
                        twoBitURI:  'https://www.biodalliance.org/datasets/GRCm38/mm10.2bit',
                        desc: 'Mouse reference genome build GRCm38',
                        tier_type: 'sequence',
                        provides_entrypoints: true
                    },
                    {
                        name: 'Genes',
                        desc: 'Gene structures from GENCODE M2',
                        bwgURI: 'https://www.biodalliance.org/datasets/GRCm38/gencodeM2.bb',
                        stylesheet_uri: 'https://www.biodalliance.org/stylesheets/gencode.xml',
                        collapseSuperGroups: true,
                        trixURI: 'https://www.biodalliance.org/datasets/GRCm38/gencodeM2.ix'
                    },
                    {
                        name: 'Repeats',
                        desc: 'Repeat annotation from UCSC',
                        bwgURI: 'https://www.biodalliance.org/datasets/GRCm38/repeats.bb',
                        stylesheet_uri: 'https://www.biodalliance.org/stylesheets/bb-repeats2.xml'
                    }
                ];
            } else if(assembly[0] == 'mm9') {
                browser.chr = '19';
                browser.viewStart = 30000000;
                browser.viewEnd = 30030000;
                browser.cookieKey = 'mouse';
                browser.coordSystem = {speciesName: 'Mouse', taxon: 10090, auth: 'NCBIM', version: 37};
                browser.sources = [
                    {
                        name: 'Genome',
                        uri:  'https://www.derkholm.net:9080/das/mm9comp/',
                        desc: 'Mouse reference genome build NCBIm37',
                        tier_type: 'sequence',
                        provides_entrypoints: true},
                    {
                        name: 'Genes',
                        desc: 'Gene structures from Ensembl 58',
                        uri:  'https://www.derkholm.net:8080/das/mmu_58_37k/',
                        collapseSuperGroups: true,
                        provides_karyotype: true,
                        provides_search: true
                    },
                    {
                        name: 'Repeats',
                        desc: 'Repeat annotation from Ensembl 58',
                        uri: 'https://www.derkholm.net:8080/das/mmu_58_37k/',
                        stylesheet_uri: 'https://www.derkholm.net/dalliance-test/stylesheets/mouse-repeats.xml'
                    }
                ];
            }
            files.forEach(function (file) {
                if(file.file_format == 'bigWig') {
                    browser.sources.push({
                        name: file.accession,
                        bwgURI: file.href + '?proxy=true',
                        style: [
                            {
                                type: 'default',
                                style: {
                                    glyph: 'HISTOGRAM',
                                    HEIGHT: 30,
                                    BGCOLOR: 'rgb(166,71,71)'
                                }
                            }
                        ]
                    });
                }
                else if(file.file_format == 'bigBed') {
                    browser.sources.push({
                        name: file.accession,
                        bwgURI: file.href + '?proxy=true',
                        style: [
                            {
                                style: {
                                    HEIGHT: 10
                                }
                            }
                        ]
                    });
                }
            });
        }.bind(this));
    },
    render: function() {
        return (
            <div id="svgHolder" className="trackhub-element">
            </div>
        );
    }
});
