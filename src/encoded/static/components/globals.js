/** @jsx React.DOM */
'use strict';
var Registry = require('registry');

// Item pages
module.exports.content_views = Registry();

// Panel detail views
module.exports.panel_views = Registry();

// Listing detail views
module.exports.listing_views = Registry();

// Cell name listing titles
module.exports.listing_titles = Registry();


var itemClass = module.exports.itemClass = function (context, htmlClass) {
    htmlClass = htmlClass || '';
    (context['@type'] || []).forEach(function (type) {
        htmlClass += ' type-' + type;
    });
    return statusClass(context.status, htmlClass);
};

var statusClass = module.exports.statusClass = function (status, htmlClass) {
    htmlClass = htmlClass || '';
    if (typeof status == 'string') {
        htmlClass += ' status-' + status.toLowerCase().replace(' ', '-');
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
