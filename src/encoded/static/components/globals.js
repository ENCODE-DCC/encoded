import _ from 'underscore';
import ga from 'google-analytics';
import Registry from '../libs/registry';

// Item pages
export const contentViews = new Registry();

// Panel detail views
export const panelViews = new Registry();

// Listing detail views
export const listingViews = new Registry();

// Cell name listing titles
export const listingTitles = new Registry();

// Blocks
export const blocks = new Registry();

// Graph detail view
export const graphDetail = new Registry();

// Search facet view
export const facetView = new Registry();

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
export const documentViews = {};
documentViews.header = new Registry();
documentViews.caption = new Registry();
documentViews.preview = new Registry();
documentViews.file = new Registry();
documentViews.detail = new Registry();

// Report-page cell components
export const reportCell = new Registry();

export function statusClass(status, htmlClass) {
    let localHtmlClass = htmlClass || '';
    if (typeof status === 'string') {
        localHtmlClass += ` status-${status.toLowerCase().replace(/ /g, '-').replace(/\(|\)/g, '')}`;
    }
    return localHtmlClass;
}

export function itemClass(context, htmlClass) {
    let localHtmlClass = htmlClass || '';
    (context['@type'] || []).forEach((type) => {
        localHtmlClass += ` type-${type}`;
    });
    return statusClass(context.status, localHtmlClass);
}

export function truncateString(str, len) {
    let localStr = str;
    if (localStr.length > len) {
        localStr = localStr.replace(/(^\s)|(\s$)/gi, ''); // Trim leading/trailing white space
        const isOneWord = str.match(/\s/gi) === null; // Detect single-word string
        localStr = localStr.substr(0, len - 1); // Truncate to length ignoring word boundary
        localStr = `${!isOneWord ? localStr.substr(0, localStr.lastIndexOf(' ')) : localStr}…`; // Back up to word boundary
    }
    return localStr;
}

// Given an array of objects with @id properties, this returns the same array but with any
// duplicate @id objects removed.
export const uniqueObjectsArray = objects => _(objects).uniq(object => object['@id']);

export function bindEvent(el, eventName, eventHandler) {
    if (el.addEventListener) {
        // Modern browsers
        el.addEventListener(eventName, eventHandler, false);
    } else if (el.attachEvent) {
        // IE8 specific
        el.attachEvent(`on${eventName}`, eventHandler);
    }
}

export function unbindEvent(el, eventName, eventHandler) {
    if (el.removeEventListener) {
        // Modern browsers
        el.removeEventListener(eventName, eventHandler, false);
    } else if (el.detachEvent) {
        // IE8 specific
        el.detachEvent(`on${eventName}`, eventHandler);
    }
}


// Encode a URI with much less intensity than encodeURIComponent but a bit more than encodeURI.
// In addition to encodeURI, this function escapes exclamations and at signs.
export function encodedURI(uri) {
    return encodeURI(uri).replace(/!/g, '%21').replace(/@/g, '%40');
}


// Just like encodeURIComponent, but also encodes parentheses (Redmine #4242). Replace spaces with
// `space` parameter, or '+' if not provided.
// http://stackoverflow.com/questions/8143085/passing-and-through-a-uri-causes-a-403-error-how-can-i-encode-them#answer-8143232
export function encodedURIComponent(str, space) {
    const spaceReplace = space || '+';
    return encodeURIComponent(str)
        .replace(/\(/g, '%28')
        .replace(/\)/g, '%29')
        .replace(/%20/g, spaceReplace)
        .replace(/%3D/g, '=');
}


// Take an @id and return the corresponding accession. If no accession could be found in the @id,
// the empty string is returned.
export function atIdToAccession(atId) {
    const matched = atId.match(/^\/.+\/(.+)\/$/);
    if (matched && matched.length === 2) {
        return matched[1];
    }
    return '';
}


/* eslint no-extend-native: ["error", { "exceptions": ["String"] }]*/
// Make the first character of the given string uppercase. Can be less fiddly than CSS text-transform.
// http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript#answer-1026087
String.prototype.uppercaseFirstChar = function uppercaseFirstChar() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};

// Convert a string to a 32-bit hash.
// http://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
export function hashCode(src) {
    let hash = 0;
    if (src.length > 0) {
        for (let i = 0; i < src.length; i += 1) {
            const char = src.charCodeAt(i);
            hash = ((hash << 5) - hash) + char; // eslint-disable-line no-bitwise
            hash &= hash; // eslint-disable-line no-bitwise
        }
    }
    return hash;
}

// Convert the number `n` to a string, zero-filled to `digits` digits. Maximum of four zeroes.
// http://stackoverflow.com/questions/2998784/how-to-output-integers-with-leading-zeros-in-javascript#answer-2998822
export function zeroFill(n, digits) {
    const filled = `0000${n}`;
    return filled.substr(filled.length - digits);
}

// Order that antibody statuses should be displayed
export const statusOrder = [
    'eligible for new data',
    'not eligible for new data',
    'pending dcc review',
    'awaiting lab characterization',
    'not pursued',
    'not reviewed',
];

export const productionHost = { 'www.encodeproject.org': 1, 'encodeproject.org': 1, 'www.encodedcc.org': 1 };

export const encodeVersionMap = {
    ENCODE2: '2',
    ENCODE3: '3',
};

// Order that assemblies should appear in lists
export const assemblyPriority = [
    'GRCh38',
    'GRCh38-minimal',
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

export const browserPriority = [
    'UCSC',
    'Ensembl',
];

// Determine the given object's ENCODE version
export function encodeVersion(context) {
    let encodevers = '';
    if (context.award && context.award.rfa) {
        encodevers = encodeVersionMap[context.award.rfa.substring(0, 7)];
        if (typeof encodevers === 'undefined') {
            encodevers = '';
        }
    }
    return encodevers;
}

// Display a human-redable form of the file size given the size of a file in bytes. Returned as a
// string.
export function humanFileSize(size) {
    if (size >= 0) {
        const i = Math.floor(Math.log(size) / Math.log(1024));
        const adjustedSize = (size / Math.pow(1024, i)).toPrecision(3) * 1;
        const units = ['B', 'kB', 'MB', 'GB', 'TB'][i];
        return `${adjustedSize} ${units}`;
    }
    return 0;
}


export function parseError(response) {
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


export function parseAndLogError(cause, response) {
    const promise = parseError(response);
    promise.then((data) => {
        ga('send', 'exception', {
            exDescription: `${cause}:${data.code}:${data.title}`,
            location: window.location.href,
        });
    });
    return promise;
}


/**
 * Sort an array of documents first by attachment download name, and then by @id.
 *
 * @param {array} docs - Array of document/characterization objects to be sorted.
 * @return (array) - Array of the same documents/characterization as was passed in, but sorted.
 */
export function sortDocs(docs) {
    return docs.sort((a, b) => {
        // Generate sorting names based on the download file name followed by the @id of the
        // document/characterization. If the document has no attachment, then this just uses the
        // the @id.
        const aLowerName = a.attachment && a.attachment.download ? a.attachment.download.toLowerCase() : '';
        const bLowerName = b.attachment && b.attachment.download ? b.attachment.download.toLowerCase() : '';
        const aAttachmentName = `${aLowerName}${a['@id']}`;
        const bAttachmentName = `${bLowerName}${b['@id']}`;

        // Perform the actual sort. Because we know the sorting name has a unique @id, we don't
        // have to check for equivalent names.
        if (aAttachmentName < bAttachmentName) {
            return -1;
        }
        return 1;
    });
}
