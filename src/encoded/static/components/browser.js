'use strict'
var React = require('react');
var $script = require('scriptjs');

module.exports.GenomeBrowser = React.createClass({
    componentDidMount: function () {
        $script('dalliance', function() {
            var Dalliance = require('dalliance').browser;
            var browser = new Dalliance({
                chr:          '22',
                viewStart:    30000000,
                viewEnd:      30030000,
                cookieKey:    'human',

                coordSystem: {
                    speciesName: 'Human',
                    taxon: 9606,
                    auth: 'NCBI',
                    version: '36',
                    ucscName: 'hg18'
                },

                noTitle: true,

                sources: [
                    {
                        name:                 'Genome',
                        uri:                  this.props.genome,
                        tier_type:            'sequence',
                        provides_entrypoints: true
                    },
                    {
                        name:                 'Genes',
                        desc:                 'Gene structures from Ensembl 54',
                        uri:                  this.props.genes,
                        collapseSuperGroups:  true,
                        provides_karyotype:   true,
                        provides_search:      true
                    },
                    {
                        name:                 'Repeats',
                        uri:                  this.props.repeats,
                        stylesheet_uri:       'http://www.derkholm.net/dalliance-test/stylesheets/ens-repeats.xml'
                    },
                    {
                        name:                 'MeDIP raw',
                        uri:                  this.props.medip
                    }
                ]
            });
        }.bind(this));
    },
    render: function() {
        return (
            <div id="svgHolder" className="trackhub-element"></div>
        );
    }
});
