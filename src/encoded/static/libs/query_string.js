/**
 * Module allowing you to conveniently modify query strings by their keys and values without
 * having to modify the actual query string itself. The general process to follow:
 *
 * const query = new QueryString(queryStringFromUrl);
 * ...modify or test `query` through public operations defined in the class...
 * query.format()
 *
 * query.format() generates a final query string based on the modifications you have made, if any.
 * The initial question mark does not get included, nor does a question mark get accepted when
 * creating the QueryString object.
 *
 * Internally, values of key/value pairs get stored in their decoded forms (i.e. spaces are
 * spaces). They get decoded when a QueryString object gets created, and only get encoded in the
 * output of format().
 */

import * as queryEncoding from './query_encoding';


class QueryString {
    constructor(query) {
        this._query = query;
        this._parse();
    }

    /**
     * Parse the `_query` string into an array of query-string elements, each one itself an array
     * with the key in the first element and the value in the second. For example, the query string
     * "type=Experiment&organism=human" becomes:
     * [['type', 'Experiment'], ['organism', 'human']]
     *
     * The order of the elements in the array maintains the order they existed in the original
     * query string.
     *
     * @return {object} Reference to this object for method chaining.
     */
    _parse() {
        // Filter out any empty elements caused by a trailing ampersand.
        const inputQueryElements = this._query.split('&').filter(element => element);
        this._parsedQuery = inputQueryElements.map((element) => {
            const keyValue = element.split('=');
            return [keyValue[0], queryEncoding.decodedURIComponent(keyValue[1])];
        });
        return this;
    }

    /**
     * Add a key/value pair to the query string. This doesn't check if the same key already exists
     * so your key can exist multiple times in the formatted query string.
     * @param {string} key Key to add to query string.
     * @param {*} value Non-URL-encoded value to add to query string. Numbers converted to strings.
     *
     * @return {object} Reference to this object for method chaining.
     */
    addKeyValue(key, value) {
        this._parsedQuery.push([key, typeof value === 'number' ? value.toString() : value]);
        return this;
    }

    /**
     * Delete any key/value pairs matching the given `key` and `value`, or all matching keys
     * regardless of their value if you don't pass `value`.
     * @param {string} key Key value to delete
     * @param {string} value Optional non-URL-encoded value to also match to delete
     *
     * @return {object} Reference to this object for method chaining.
     */
    deleteKeyValue(key, value) {
        this._parsedQuery = this._parsedQuery.filter(element => element[0] !== key || (value !== undefined ? element[1] !== value : false));
        return this;
    }

    /**
     * Replace any key/value pairs matching the given `key` with the given `value`, so if multiple
     * existing key/value pairs match the given key, they all get removed and replaced by this new
     * key/value pair.
     * @param {string} key Key value to replace
     * @param {string} value Non-URL-encoded value to replace
     *
     * @param {object} Reference to this object for method chaining.
     */
    replaceKeyValue(key, value) {
        this.deleteKeyValue(key).addKeyValue(key, value);
        return this;
    }

    /**
     * Return an array of values whose keys match the `key` string parameter. For example, for the
     * query string "a=1&b=2&a=3" the resulting array for `key` of "a" is [1, 3], and a `key` of"b"
     * would lead to [2].
     * @param {string} key Key whose values get returned.
     *
     * @return {array} Non-URL-encoded values that have `key` as their key.
     */
    getKeyValues(key) {
        return this._parsedQuery.filter(queryElement => queryElement[0] === key).map(queryElement => queryElement[1]);
    }

    /**
     * Return key/value pairs for query-string elements whose keys do NOT match the `key` string
     * parameter. For example, for the query string "a=1&b=2&a=3" the resulting object for `key`
     * of "b" is { a: [1, 3] } and for `key` of "a" is { b: 2 }. Note that keys that occur
     * multiple times in the query string have an array as their value in the object returned by
     * this function.
     * @param {string} key Key whose values get returned.
     *
     * @return {object} Key/value pairs that don't have `key` as their key.
     */
    getNotKeyElements(key) {
        const notElements = this._parsedQuery.filter(queryElement => queryElement[0] !== key);
        const notKeyValues = {};
        notElements.forEach((element) => {
            if (notKeyValues[element[0]]) {
                // We have seen this key before. Convert its value to an array if the current
                // value is a single value, or add to the key's array if the key already has
                // multiple values.
                if (typeof notKeyValues[element[0]] === 'object') {
                    // Key already has multiple values, so add to that array.
                    notKeyValues[element[0]].push(element[1]);
                } else {
                    // Key has a single value, so convert that and new value to an array.
                    notKeyValues[element[0]] = [notKeyValues[element[0]], element[1]];
                }
            } else {
                // Haven't seen this key before; just assign its (so far) single value.
                notKeyValues[element[0]] = element[1];
            }
        });
        return notKeyValues;
    }

    /**
     * Get the query string corresponding to the query this object holds. If you have made no
     * modifications to the query this object holds, you get back the same query string that
     * initialized this object.
     *
     * @return {string} Equivalent query string.
     */
    format() {
        return this._parsedQuery.map(queryElement => `${queryElement[0]}=${queryEncoding.encodedURIComponent(queryElement[1])}`).join('&');
    }
}

export default QueryString;
