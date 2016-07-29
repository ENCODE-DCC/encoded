'use strict';
var Registry = require('../libs/registry');
var _ = require('underscore');

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

// Graph detail view
module.exports.graph_detail = new Registry();

// Document panel components
// +---------------------------------------+
// | header                                |
// +---------------------------+-----------+
// |                           |           |
// |          caption          |  preview  |
// |                           |           |
// +---------------------------+-----------+
// | file                                  |
// +---------------------------------------+
// | detail                                |
// +---------------------------------------+
var document_views = {};
document_views.header = new Registry();
document_views.caption = new Registry();
document_views.preview = new Registry();
document_views.file = new Registry();
document_views.detail = new Registry();
module.exports.document_views = document_views;

// Report-page cell components
module.exports.report_cell = new Registry();

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
        htmlClass += ' status-' + status.toLowerCase().replace(/ /g, '-').replace(/\(|\)/g,'');
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

// Given an array of objects with @id properties, this returns the same array but with any
// duplicate @id objects removed.
module.exports.uniqueObjectsArray = objects => _(objects).uniq(object =>  object['@id']);

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

module.exports.unreleased_files_url = function (context) {
    var file_states = [
        '',
        "uploading",
        "uploaded",
        "upload failed",
        "format check failed",
        "in progress",
        "released",
        "archived"
    ].map(encodeURIComponent).join('&status=');
    return '/search/?limit=all&type=file&dataset=' + context['@id'] + file_states;
};


// Just like encodeURIComponent, but also encodes parentheses (Redmine #4242). Replace spaces with
// `space` parameter, or '+' if not provided.
// http://stackoverflow.com/questions/8143085/passing-and-through-a-uri-causes-a-403-error-how-can-i-encode-them#answer-8143232
var encodedURIComponent = module.exports.encodedURIComponent = function(str, space) {
    var spaceReplace = space ? space : '+';
    return encodeURIComponent(str).replace(/\(/g, '%28').replace(/\)/g, '%29').replace(/%20/g, spaceReplace);
};

// Make the first character of the given string uppercase. Can be less fiddly than CSS text-transform.
// http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript#answer-1026087
String.prototype.uppercaseFirstChar = function(string) {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

// Convert the number `n` to a string, zero-filled to `digits` digits. Maximum of four zeroes.
// http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript#answer-2998822
module.exports.zeroFill = function(n) {
    var filled = '0000' + n;
    return filled.substr(filled.length - 4);
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

var encodeVersionMap = module.exports.encodeVersionMap = {
    "ENCODE2": "2",
    "ENCODE3": "3"
};

// Determine the given object's ENCODE version
module.exports.encodeVersion = function(context) {
    var encodevers = "";
    if (context.award && context.award.rfa) {
        encodevers = encodeVersionMap[context.award.rfa.substring(0,7)];
        if (typeof encodevers === "undefined") {
            encodevers = "";
        }
    }
    return encodevers;
};

module.exports.dbxref_prefix_map = {
    "UniProtKB": "http://www.uniprot.org/uniprot/",
    "HGNC": "http://www.genecards.org/cgi-bin/carddisp.pl?gene=",
    // ENSEMBL link only works for human
    "ENSEMBL": "http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=",
    "GeneID": "http://www.ncbi.nlm.nih.gov/gene/",
    "GEO": "http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=",
    "GEOSAMN": "http://www.ncbi.nlm.nih.gov/biosample/",
    "IHEC": "http://www.ebi.ac.uk/vg/epirr/view/",
    "Caltech": "http://jumpgate.caltech.edu/library/",
    "Cellosaurus": "http://web.expasy.org/cellosaurus/",
    "FlyBase": "http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context=",
    // This WormBase link is strictly for Fly strains
    "FlyBaseStock": "http://flybase.org/reports/",
    "BDSC": "http://flystocks.bio.indiana.edu/Reports/",
    "WormBaseTargets": "http://www.wormbase.org/species/c_elegans/gene/",
    // This WormBase link is strictly for C. elegans strains
    "WormBase": "http://www.wormbase.org/species/c_elegans/strain/",
    "NBP": "http://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq=",
    "CGC": "http://www.cgc.cbs.umn.edu/search.php?st=",
    "DSSC": "https://stockcenter.ucsd.edu/index.php?action=view&q=",
    "MGI": "http://www.informatics.jax.org/marker/",
    "MGI.D": "http://www.informatics.jax.org/external/festing/mouse/docs/",
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
    "doi": "http://dx.doi.org/doi:",
    // Antibody RRids
    "AR": "http://antibodyregistry.org/search.php?q="
};
