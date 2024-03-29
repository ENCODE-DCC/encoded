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
    /**
     * Find the value of the key in a parsed QueryString element. Each element (documented in
     * `_parse`) is an object with the query-string key as the object key and the query-string
     * value as this object key's value, as well as a `negative` boolean.
     * @param {object} queryElement One parsed element of a QueryString object
     * @returns {string} Value of the key in an element of a parsed QueryString object
     */
    static _getQueryElementKey(queryElement) {
        return Object.keys(queryElement).find((key) => key !== 'negative');
    }

    /**
     * Compare two `QueryString` objects to see if they represent the same query. The two query
     * strings don't need to have their elements in the same order to consider them equal -- they
     * simply need to have the same keys and values, and the same negations ("=" vs "!=") for each.
     * If `isExact` is true, then the two query strings must also have the same number of elements.
     * Otherwise, `equal()` returns true if `query1` has all the elements of `query2` even if
     * `query2` has other elements not in `query1`. `equal()` might not return the correct value if
     * either query string has repeated key/element values.
     * @param {QueryString} query1 First QueryString object to compare
     * @param {QueryString} query2 Second QueryString object to compare
     * @param {boolean} isExact True to match all keys/values exactly; false to match key subset
     * @returns {boolean} True if the two query strings represent the same query
     */
    static equal(query1, query2, isExact = true) {
        const isSubsetMatching = query1._parsedQuery.reduce((equal, query1Element) => {
            if (equal) {
                // Find the key this element represents. Assume it exists; we have a bug if not.
                const query1Key = QueryString._getQueryElementKey(query1Element);

                // So far only equal elements have been found. Search query2 for an element
                // matching an element from query1.
                const equalElement = query2._parsedQuery.find((query2Element) => {
                    const query2Key = QueryString._getQueryElementKey(query2Element);
                    return (
                        query1Key === query2Key
                        && query1Element[query1Key] === query2Element[query2Key]
                        && query1Element.negative === query2Element.negative
                    );
                });
                return !!equalElement;
            }

            // Once we can't find an equal element, we can stop searching.
            return false;
        }, true);

        return (
            isExact
                ? isSubsetMatching && query1._parsedQuery.length === query2._parsedQuery.length
                : isSubsetMatching
        );
    }

    constructor(query) {
        this._query = query;
        this._parse();
    }

    /**
     * Parse the `_query` string into an array of query-string elements, each an object with the
     * query-string key becoming a key in the object with the query-string value its value, and a
     * `negative` key false for a=b query string parameters, and true for a!=b. For example, the
     * query string "type=Experiment&organism=human&assay!=ChIP-seq" becomes:
     * [{
     *     type: 'Experiment',
     *     negative: false,
     * }, {
     *     organism: 'human',
     *     negative: false,
     * }, {
     *     assay: 'ChIP-seq',
     *     negative: true,
     * }]
     *
     * The order of the elements in the array maintains the order they existed in the original
     * query string.
     *
     * @return {object} Reference to this object for method chaining.
     */
    _parse() {
        // Filter out any empty elements caused by a trailing ampersand.
        if (this._query) {
            const inputQueryElements = this._query.split('&').filter((element) => element);
            this._parsedQuery = inputQueryElements.map((element) => {
                // Split each query string element into its key and value in `queryElement`. If "!"
                // is at the end of the key, then this was a != query-string element. In that case
                // set the `negative` property in `queryElement` and strip the "!" from the key.
                const queryElement = {};
                const keyValue = element.split('=');
                const negationMatch = keyValue[0].match(/(.*?)(%21|!)*$/);
                queryElement[negationMatch[1]] = queryEncoding.decodedURIComponent(keyValue[1]);
                queryElement.negative = negationMatch[2] === '%21' || negationMatch[2] === '!';
                return queryElement;
            });
        } else {
            this._parsedQuery = [];
        }
        return this;
    }

    /**
     * Add a key/value pair to the query string. This doesn't check if the same key already exists
     * so your key can exist multiple times in the formatted query string.
     * @param {string} key Key to add to query string.
     * @param {*} value Non-URL-encoded value to add to query string. Numbers converted to strings.
     * @param {bool} negative: True if negative query (a!=b)
     *
     * @return {object} Reference to this object for method chaining.
     */
    addKeyValue(key, value, negative) {
        const keyValue = {};
        keyValue[key] = typeof value === 'number' ? value.toString() : value;
        keyValue.negative = !!negative; // Caller might pass anything; want true/false
        this._parsedQuery.push(keyValue);
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
        this._parsedQuery = this._parsedQuery.filter((element) => element[key] === undefined || (value !== undefined ? element[key] !== value : false));
        return this;
    }

    /**
     * Replace any key/value pairs matching the given `key` with the given `value`, so if multiple
     * existing key/value pairs match the given key, they all get removed and replaced by this new
     * key/value pair.
     * @param {string} key Key value to replace
     * @param {string} value Non-URL-encoded value to replace
     * @param {bool} negative True if new key/value is a negative (a!=b)
     *
     * @param {object} Reference to this object for method chaining.
     */
    replaceKeyValue(key, value, negative) {
        this.deleteKeyValue(key).addKeyValue(key, value, negative);
        return this;
    }

    /**
     * Return an array of values whose keys match the `key` string parameter. For example, for the
     * query string "a=1&b=2&a=3&b!=3" the resulting array for `key` of "a" returns [1, 3], and a
     * `key` of "b" would return [2]. If you pass `negative` as true, then a `key` of "a" is [] and
     * a `key` of "b" return [3].
     * @param {string} key Key whose values get returned.
     * @param {bool} negative True to return negative matches for `key`.
     *
     * @return {array} Non-URL-encoded values that have `key` as their key.
     */
    getKeyValues(key, negative) {
        return this._parsedQuery.filter((queryElement) => queryElement[key] && queryElement.negative === !!negative).map((queryElement) => queryElement[Object.keys(queryElement)[0]]);
    }

    /**
     * Returns an array of values whose keys match the `key` string parameter REGARDLESS of the relationship
     * between the key and value in the query string. For example, query string "a=1&b=2&a=3&b!=3", a `key`
     * value of "b" would return [2,3]. This method does not take "==" and "!=" into consideration.
     * @param {string} key
     * @memberof QueryString
     *
     *  @return {array} Non-URL-encoded values that have `key` as their key.
     */
    getKeyValuesIfPresent(key) {
        return this._parsedQuery
            .filter((queryElement) => queryElement[key])
            .map((queryElement) => queryElement[Object.keys(queryElement)[0]]);
    }

    /**
     * Get the number of query string elements for any key or a specific key.
     * @param {string} key Optional key to count; count all keys if not supplied
     *
     * @return {number} Count of query string elements.
     */
    queryCount(key) {
        if (key) {
            return this._parsedQuery.filter((queryElement) => queryElement[key]).length;
        }
        return this._parsedQuery.length;
    }

    /**
     * Get the query string corresponding to the query this object holds. If you have made no
     * modifications to the query this object holds, you get back the same query string that
     * initialized this object.
     *
     * @return {string} Equivalent query string.
     */
    format() {
        return this._parsedQuery.map((queryElement) => {
            const key = Object.keys(queryElement)[0];
            return `${key}${queryElement.negative ? '!=' : '='}${queryEncoding.encodedURIComponent(queryElement[key])}`;
        }).join('&');
    }

    /**
     * Make a clone of this query string object that can be manipulated independently of this one.
     *
     * @return {object} Cloned QueryString object.
     */
    clone() {
        return new QueryString(this.format());
    }
}

export default QueryString;
