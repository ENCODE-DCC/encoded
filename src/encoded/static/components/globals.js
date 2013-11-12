/** @jsx React.DOM */
'use strict';
var Registry = require('registry');

    // Item pages
    module.exports.content_views = Registry();

    // Panel detail views
    module.exports.panel_views = Registry();

    // Cell name listing titles
    module.exports.listing_titles = Registry();


    module.exports.itemClass = function (context, htmlClass) {
        htmlClass = htmlClass || '';
        (context['@type'] || []).forEach(function (type) {
            htmlClass += ' type-' + type;
        });
        if (typeof context.status == 'string') {
            htmlClass += ' status-' + context.status.toLowerCase();
        }
        return htmlClass;
    };

    module.exports.dbxref_prefix_map = {
        "UniProtKB": "http://www.uniprot.org/uniprot/",
        "HGNC": "http://www.genecards.org/cgi-bin/carddisp.pl?gene=",
        // ENSEMBL link only works for human
        "ENSEMBL": "http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=",
        "GeneID": "http://www.ncbi.nlm.nih.gov/gene/",
        "GEO": "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=",
        "Caltech": "http://jumpgate.caltech.edu/library/"
    };
