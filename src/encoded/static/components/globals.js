import _ from 'underscore';
import ga from 'google-analytics';
import url from 'url';
import Registry from '../libs/registry';
import DataColors from './datacolors';

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

export function itemClass(context, htmlClass) {
    let localHtmlClass = htmlClass || '';
    (context['@type'] || []).forEach((type) => {
        localHtmlClass += ` type-${type}`;
    });
    return localHtmlClass;
}

export function truncateString(str, len) {
    let localStr = str;
    if (localStr.length > len) {
        localStr = localStr.replace(/(^\s)|(\s$)/gi, ''); // Trim leading/trailing white space
        localStr = localStr.substr(0, len - 1); // Truncate to length ignoring word boundary
        const isOneWord = localStr.match(/\s/gi) === null; // Detect single-word string
        localStr = `${!isOneWord ? localStr.substr(0, localStr.lastIndexOf(' ')) : localStr}…`; // Ensure last word is not prematurely split
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


/**
 * Remove spaces from id so it can be accepted as an id by HTML
 *
 * @param {string} id
 * @returns id without space or dash if id is empty
 */
export const sanitizeId = id => (id ? `${id.replace(/\s/g, '_')}` : '-');


// Take an @id and return the corresponding accession. If no accession could be found in the @id,
// the empty string is returned.
export function atIdToAccession(atId) {
    const matched = atId.match(/^\/.+\/(.+)\/$/);
    if (matched && matched.length === 2) {
        return matched[1];
    }
    return atId;
}


// Take an @id and return the corresponding object type. If no object type could be found in the
// @id, the empty string is returned.
export function atIdToType(atId) {
    const matched = atId.match(/^\/(.+)\/.+\/$/);
    if (matched && matched.length === 2) {
        return matched[1];
    }
    return '';
}


// Make the first character of the given string uppercase. Can be less fiddly than CSS text-transform.
// http://stackoverflow.com/questions/1026069/capitalize-the-first-letter-of-string-in-javascript#answer-1026087
/* eslint-disable no-extend-native */
String.prototype.uppercaseFirstChar = function uppercaseFirstChar() {
    return this.charAt(0).toUpperCase() + this.slice(1);
};
/* eslint-enable no-extend-native */

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

// Convert a status string to a string suitable to build a CSS class name.
export const statusToClassElement = status => status.toLowerCase().replace(/ /g, '-').replace(/\(|\)/g, '');


/**
 * Returns true if code runs on the production host, as opposed to test, demos, or local. This
 * applies to both server and browser rendering.
 * @param {string} currentUrl Normally from React context.location_href
 *
 * @return True if code runs on production host
 */
export const isProductionHost = currentUrl => (
    ['www.encodeproject.org', 'encodeproject.org', 'www.encodedcc.org'].includes(url.parse(currentUrl).hostname)
);

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

export function getRoles(sessionProperties) {
    // handles {}, null and other signs of lacks of content
    if (_.isEmpty(sessionProperties)) {
        return [];
    }

    const roles = [];

    // non-empty auth.userid-object shows user is logged at least, so has unprivileged rights
    if (sessionProperties['auth.userid']) {
        roles.push('unprivileged');
    }

    if (sessionProperties.admin) {
        roles.push('admin');
    }

    const userSessionProperties = sessionProperties.user;

    if (userSessionProperties &&
            userSessionProperties.lab &&
            userSessionProperties.lab.status === 'current' &&
            userSessionProperties.submits_for &&
            userSessionProperties.submits_for.length > 0) {
        roles.push('submitter');
    }

    return roles;
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


export const dbxrefPrefixMap = {
    FlyBase: 'http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context=',
    WormBase: 'http://www.wormbase.org/species/c_elegans/strain/',
};


// Sanitize user input and facet terms for comparison: convert to lowercase, remove white space and asterisks (which cause regular expression error)
export const sanitizedString = inputString => inputString.toLowerCase()
    .replace(/ /g, '') // remove spaces (to allow multiple word searches)
    .replace(/[*?()+[\]\\/]/g, ''); // remove certain special characters (these cause console errors)


// Keep lists of currently known project and biosample_type. As new project and biosample_type
// enter the system, these lists must be updated. Used mostly to keep chart and matrix colors
// consistent.
export const projectList = [
    'ENCODE',
    'Roadmap',
    'modENCODE',
    'modERN',
    'GGR',
];

export const biosampleTypeList = [
    'cell line',
    'tissue',
    'primary cell',
    'whole organisms',
    'in vitro differentiated cells',
    'single cell',
    'cell-free sample',
    'cloning host',
    'organoid',
];

export const replicateTypeList = [
    'unreplicated',
    'isogenic',
    'anisogenic',
];


// Make `project` and `biosample_type` color mappings for downstream modules to use.
export const projectColors = new DataColors(projectList);
export const biosampleTypeColors = new DataColors(biosampleTypeList);
export const replicateTypeColors = new DataColors(replicateTypeList);


// Map view icons to svg icons.
export const viewToSvg = {
    'list-alt': 'search',
    table: 'table',
    summary: 'summary',
    th: 'matrix',
};


// Media query breakpoints to match those in style.scss.
const SCREEN_XS = 480;
const SCREEN_SM = 768;
const SCREEN_MD = 960;
const SCREEN_LG = 1160;
const SCREEN_XL = 1716;


/**
 * Determine whether the current browser-window width activates the given Bootstrap-based media
 * query code. The component this function gets called from must have mounted.
 * @param min {string} Bootstrap-based code for each breakpoint
 *
 * @return {bool} True if specified breakpoint is active
 */
export const isMediaQueryBreakpointActive = (min) => {
    if (window.matchMedia) {
        let breakpoint;
        switch (min) {
        case 'XS':
            breakpoint = SCREEN_XS;
            break;
        case 'SM':
            breakpoint = SCREEN_SM;
            break;
        case 'MD':
            breakpoint = SCREEN_MD;
            break;
        case 'LG':
            breakpoint = SCREEN_LG;
            break;
        case 'XL':
            breakpoint = SCREEN_XL;
            break;
        default:
            // Undefined code; default to mobile.
            breakpoint = 0;
        }
        const mql = window.matchMedia(`(min-width: ${breakpoint}px)`);
        return mql.matches;
    }

    // Browser doesn't support matchMedia, so default to mobile.
    return false;
};
