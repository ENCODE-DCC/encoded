/**
 * Just like encodeURIComponent, but does encoded-specific character replacement to avoid 301
 * redirects. Only use this for the value on the right side of the query-string key-value equals
 * sign.
 * http://stackoverflow.com/questions/8143085/passing-and-through-a-uri-causes-a-403-error-how-can-i-encode-them#answer-8143232
 * @param {string} value Query-string value that needs encoding
 *
 * @return {string} URL-encoded query-string value.
 */
export const encodedURIComponent = value => (
    encodeURIComponent(value)
        .replace(/\(/g, '%28')
        .replace(/\)/g, '%29')
        .replace(/%3A/g, ':')
        .replace(/%20/g, '+')
);


/**
 * Just like decodeURIComponent, but also converts plus signs into spaces. This function acts as
 * the complement to encodedURIComponent above.
 * @param {string} value URL-encoded value from a key-value query-string pair
 *
 * @return {string} Unencoded query-string value
 */
export const decodedURIComponent = value => (
    decodeURIComponent(value.replace(/\+/g, '%20'))
);


// Encode a URI with much less intensity than encodeURIComponent but a bit more than encodeURI.
// In addition to encodeURI, this function escapes exclamations and at signs.
// ! Do not use this function; all usage should move to encodedURIComponent.
export function encodedURIOLD(uri) {
    return encodeURI(uri).replace(/!/g, '%21').replace(/@/g, '%40');
}


// Just like encodeURIComponent, but also encodes parentheses (Redmine #4242). Replace spaces with
// `options.space` parameter, or '+' if not provided. Encodes equals sign if `options.encodeEquals`
// set to true, or leaves the equals sign unencoded.
// http://stackoverflow.com/questions/8143085/passing-and-through-a-uri-causes-a-403-error-how-can-i-encode-them#answer-8143232
// ! Do not use this function; all usage should move to encodedURIComponent.
export function encodedURIComponentOLD(str, options = {}) {
    const spaceReplace = options.space || '+';
    const preEquals = encodeURIComponent(str)
        .replace(/\(/g, '%28')
        .replace(/\)/g, '%29')
        .replace(/%20/g, spaceReplace);
    return options.encodeEquals ? preEquals : preEquals.replace(/%3D/g, '=');
}
