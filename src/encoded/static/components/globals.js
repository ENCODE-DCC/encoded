define(['exports', 'registry'],
function (globals, Registry) {
    /*jshint devel: true*/
    'use strict';

    // Item pages
    globals.content_views = Registry();

    // Panel detail views
    globals.panel_views = Registry();

    // Cell name listing titles
    globals.listing_titles = Registry();


    globals.itemClass = function (context, htmlClass) {
        htmlClass = htmlClass || '';
        (context['@type'] || []).forEach(function (type) {
            htmlClass += ' type-' + type;
        });
        if (typeof context.status == 'string') {
            htmlClass += ' status-' + context.status.toLowerCase();
        }
        return htmlClass;
    };

    globals.dbxref_prefix_map = {
        "UniProtKB": "http://www.uniprot.org/uniprot/",
        "HGNC": "http://www.genecards.org/cgi-bin/carddisp.pl?id_type=hgnc&=",
        // ENSEMBL link only works for human
        "ENSEMBL": "http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=",
        "GeneID": "http://www.ncbi.nlm.nih.gov/gene/",
        "GEO": "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=",
        "Caltech": "http://jumpgate.caltech.edu/library/"
    };

    return globals;
});
