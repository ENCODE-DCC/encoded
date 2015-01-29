/** @jsx React.DOM */
'use strict';
var Registry = require('../libs/registry');

// Item pages
module.exports.content_views = new Registry();

// Panel detail views
module.exports.panel_views = new Registry();

// Listing detail views
module.exports.listing_views = new Registry();

// Cell name listing titles
module.exports.listing_titles = new Registry();

// Blocks
module.exports.blocks = new Registry();


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
        htmlClass += ' status-' + status.toLowerCase().replace(/ /g, '-');
    }
    return htmlClass;
};

var validationStatusClass = module.exports.validationStatusClass = function (status, htmlClass) {
    htmlClass = htmlClass || '';
    if (typeof status == 'string') {
        htmlClass += ' validation-status-' + status.toLowerCase().replace(/ /g, '-');
    }
    return htmlClass;
};

module.exports.truncateString = function (str, len) {
    if (str.length > len) {
        str = str.replace(/(^\s)|(\s$)/gi, ''); // Trim leading/trailing white space
        var isOneWord = str.match(/\s/gi) === null; // Detect single-word string
        str = str.substr(0, len - 1); // Truncate to length ignoring word boundary
        str = (!isOneWord ? str.substr(0, str.lastIndexOf(' ')) : str) + '…'; // Back up to word boundary
    }
    return str;
};

module.exports.bindEvent = function (el, eventName, eventHandler) {
    if (el.addEventListener) {
        // Modern browsers
        el.addEventListener(eventName, eventHandler, false); 
    } else if (el.attachEvent) {
        // IE8 specific
        el.attachEvent('on' + eventName, eventHandler);
    }
};

module.exports.unbindEvent = function (el, eventName, eventHandler) {
    if (el.removeEventListener) {
        // Modern browsers
        el.removeEventListener(eventName, eventHandler, false); 
    } else if (el.detachEvent) {
        // IE8 specific
        el.detachEvent('on' + eventName, eventHandler);
    }
};

// Order that antibody statuses should be displayed
module.exports.statusOrder = [
    'eligible for new data',
    'not eligible for new data',
    'pending dcc review',
    'awaiting lab characterization',
    'not pursued',
    'not reviewed'
];


module.exports.productionHost = {'www.encodeproject.org':1, 'encodeproject.org':1, 'www.encodedcc.org':1};

module.exports.encodeVersionMap = {
    "ENCODE2": "2",
    "ENCODE3": "3"
};

module.exports.dbxref_prefix_map = {
    "UniProtKB": "http://www.uniprot.org/uniprot/",
    "HGNC": "http://www.genecards.org/cgi-bin/carddisp.pl?gene=",
    // ENSEMBL link only works for human
    "ENSEMBL": "http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=",
    "GeneID": "http://www.ncbi.nlm.nih.gov/gene/",
    "GEO": "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=",
    "Caltech": "http://jumpgate.caltech.edu/library/",
    "FlyBase": "http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context=",
    "WormBase": "http://www.wormbase.org/species/c_elegans/gene/",
    "RefSeq": "http://www.ncbi.nlm.nih.gov/gene/?term=",
    // UCSC links need assembly (&db=) and accession (&hgt_mdbVal1=) added to url
    "UCSC-ENCODE-mm9": "http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=mm9&hgt_mdbVal1=",
    "UCSC-ENCODE-hg19": "http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=",
    "UCSC-ENCODE-cv": "http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term=",
    "UCSC-GB-mm9": "http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=mm9&g=",
    "UCSC-GB-hg19": "http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=",
    // Dataset, experiment, and document references
    "PMID": "http://www.ncbi.nlm.nih.gov/pubmed/?term=",
    "PMCID": "http://www.ncbi.nlm.nih.gov/pmc/articles/",
    "doi": "http://dx.doi.org/doi:"
};
