'use strict';
var Registry = require('../libs/registry');
var _ = require('underscore');
const ga = require('google-analytics');

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

// Search facet view
module.exports.facet_view = new Registry();

// Document panel components
// +---------------------------------------+
// | header                                |
// +---------------------------+-----------+
// |                           |           |
// |          caption          |  preview  | <--This row Called a document "intro" in the code
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
module.exports.uniqueObjectsArray = objects => _(objects).uniq(object => object['@id']);

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
        "archived",
        "content error",
    ].map(encodeURIComponent).join('&status=');
    return '/search/?limit=all&type=File&dataset=' + context['@id'] + file_states;
};


// Encode a URI with much less intensity than encodeURIComponent but a bit more than encodeURI.
// In addition to encodeURI, this function escapes exclamations and at signs.
module.exports.encodedURI = function (uri) {
    return encodeURI(uri).replace(/!/g, '%21').replace(/@/g, '%40');
};

 
// Just like encodeURIComponent, but also encodes parentheses (Redmine #4242). Replace spaces with
// `space` parameter, or '+' if not provided.
// http://stackoverflow.com/questions/8143085/passing-and-through-a-uri-causes-a-403-error-how-can-i-encode-them#answer-8143232
module.exports.encodedURIComponent = function (str, space) {
    const spaceReplace = space || '+';
    return encodeURIComponent(str).replace(/\(/g, '%28').replace(/\)/g, '%29').replace(/%20/g, spaceReplace).replace(/%3D/g, '=');
};


// Take an @id and return the corresponding accession. If no accession could be found in the @id,
// the empty string is returned.
module.exports.atIdToAccession = function (atId) {
    const matched = atId.match(/^\/.+\/(.+)\/$/);
    if (matched && matched.length === 2) {
        return matched[1];
    }
    return '';
};


// Make the first character of the given string uppercase. Can be less fiddly than CSS text-transform.
// http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript#answer-1026087
String.prototype.uppercaseFirstChar = function(string) {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

// Convert a string to a 32-bit hash.
// http://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
module.exports.hashCode = function (src) {
    let hash = 0;
    if (src.length > 0) {
        for (let i = 0; i < src.length; i += 1) {
            const char = src.charCodeAt(i);
            hash = ((hash << 5) - hash) + char; // eslint-disable-line no-bitwise
            hash &= hash; // eslint-disable-line no-bitwise
        }
    }
    return hash;
};

// Convert the number `n` to a string, zero-filled to `digits` digits. Maximum of four zeroes.
// http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript#answer-2998822
module.exports.zeroFill = function(n, digits) {
    var filled = '0000' + n;
    return filled.substr(filled.length - digits);
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

// Order that assemblies should appear in lists
module.exports.assemblyPriority = [
    'GRCh38',
    'hg19',
    'mm10',
    'mm10-minimal',
    'mm9',
    'ce11',
    'ce10',
    'dm6',
    'dm3',
    'J02459.1',
];

module.exports.browserPriority = [
    'UCSC',
    'Ensembl',
];

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

// Display a human-redable form of the file size given the size of a file in bytes. Returned as a
// string.
module.exports.humanFileSize = function (size) {
    if (size >= 0) {
        const i = Math.floor(Math.log(size) / Math.log(1024));
        const adjustedSize = (size / Math.pow(1024, i)).toPrecision(3) * 1;
        const units = ['B', 'kB', 'MB', 'GB', 'TB'][i];
        return `${adjustedSize} ${units}`;
    }
}


const parseError = function (response) {
    if (response instanceof Error) {
        return Promise.resolve({
            status: 'error',
            title: response.message,
            '@type': ['AjaxError', 'Error'],
        });
    }
    let contentType = response.headers.get('Content-Type') || '';
    contentType = contentType.split(';')[0];
    if (contentType === 'application/json') {
        return response.json();
    }
    return Promise.resolve({
        status: 'error',
        title: response.statusText,
        code: response.status,
        '@type': ['AjaxError', 'Error'],
    });
}
module.exports.parseError = parseError;

module.exports.parseAndLogError = function (cause, response) {
    const promise = parseError(response);
    promise.then((data) => {
        ga('send', 'exception', {
            exDescription: `${cause}:${data.code}:${data.title}`,
            location: window.location.href,
        });
    });
    return promise;
}

module.exports.dbxref_prefix_map = {
    "UniProtKB": "http://www.uniprot.org/uniprot/",
    "HGNC": "http://www.genecards.org/cgi-bin/carddisp.pl?gene=",
    // ENSEMBL link only works for human
    "ENSEMBL": "http://www.ensembl.org/Homo_sapiens/Gene/Summary?g=",
    "GeneID": "https://www.ncbi.nlm.nih.gov/gene/",
    "GEO": "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=",
    "GEOSAMN": "https://www.ncbi.nlm.nih.gov/biosample/",
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
    "RBPImage":"http://rnabiology.ircm.qc.ca/RBPImage/gene.php?cells=",
    "RefSeq": "https://www.ncbi.nlm.nih.gov/gene/?term=",
    // UCSC links need assembly (&db=) and accession (&hgt_mdbVal1=) added to url
    "UCSC-ENCODE-mm9": "http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=mm9&hgt_mdbVal1=",
    "UCSC-ENCODE-hg19": "http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1=",
    "UCSC-ENCODE-cv": "http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term=",
    "UCSC-GB-mm9": "http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=mm9&g=",
    "UCSC-GB-hg19": "http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g=",
    // Dataset, experiment, and document references
    "PMID": "https://www.ncbi.nlm.nih.gov/pubmed/?term=",
    "PMCID": "https://www.ncbi.nlm.nih.gov/pmc/articles/",
    "doi": "http://dx.doi.org/doi:",
    // Antibody RRids
    "AR": "http://antibodyregistry.org/search.php?q=",
    // NIH stem cell
    "NIH": "https://search.usa.gov/search?utf8=%E2%9C%93&affiliate=grants.nih.gov&query=",
};
