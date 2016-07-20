var _ = require('underscore');


var querystring = {
    // Parse a query string and convert it to an object, with the query string parameters as the
    // keys and their values as the corresponding values in the object. If a key appears more than
    // once in a query string, then it appears as a key once in the resulting object, and the
    // different values appear as an array of values for that key.
    parse: function(query) {
        // Find the '?' and start parsing from there.
        var decodedQuery = decodeURIComponent(query);
        var start = decodedQuery.indexOf('?');
        decodedQuery = decodedQuery.substring(start + 1);

        // Break into query parameters.
        var parsed = decodedQuery.split('&');
        var parsedObj = {};
        parsed.forEach(parm => {
            // Find the last instance of '=' in query parameter.
            var equalInd = parm.lastIndexOf('=');
            if (equalInd > 0) {
                // Extract key and value around '='.
                var key = parm.substring(0, equalInd);
                var value = parm.substring(equalInd + 1);

                // Add key to parsedObj with its value. Need to make array of values if more than
                // one instance of any key.
                if (parsedObj[key]) {
                    // Already seen this key. Need to add new value.
                    if (typeof parsedObj[key] === 'object') {
                        // Already saw more than one of this key; add new key to array of values.
                        parsedObj[key].push(value);
                    } else {
                        // Only saw this key once. Convert existing value to array of two values.
                        parsedObj[key] = [parsedObj[key], value];
                    }
                } else {
                    // Never saw this key before
                    parsedObj[key] = value;
                }
            }
        });
        return parsedObj;
    },

    // Returns true if the parsed query string object (`parsedObj`) contains a matching key and
    // value.
    keyValueExists: function(parsedObj, key, value) {
        if (parsedObj[key]) {
            if (typeof parsedObj[key] === 'object') {
                // Key has more than one value. See if a matching value is in the array ov values.
                return _(parsedObj[key]).find(parsedVal => parsedVal === value);
            } else {
                return parsedObj[key] === value;
            }
        }
    },

    // Delete one key/value combination from the parsed query string object passed in `parsedObj`.
    // If the value is one of multiple values for that key, just that value is deleted -- its key
    // remains.
    deleteValue: function(parsedObj, key, value) {
        if (parsedObj[key]) {
            if (typeof parsedObj[key] === 'object') {
                // Array of values; find and delete the matching one(s).
                parsedObj[key] = parsedObj[key].filter(extantValue => extantValue !== value);
                if (parsedObj[key].length === 1) {
                    // Leaves only one value in the array; make it a string instead.
                    parsedObj[key] = parsedObj[key][0];
                }
            } else if (parsedObj[key] === value) {
                // A single string value: delete it and its key from the object
                delete parsedObj[key];
            }
        }
        return parsedObj;
    },

    // Delete one key from the parsed query string object passed in `parsedObj`. If more than one
    // value exists for that key, that key and all its values are deleted. 
    deleteKey: function(parsedObj, key) {
        if (parsedObj[key]) {
            delete parsedObj[key];
        }
        return parsedObj;
    },

    // Convert a parsed query string object back into a query string, starting with the '?'.
    stringify: function(parsedObj) {
        var str = '';
        Object.keys(parsedObj).forEach(key => {
            if (typeof parsedObj[key] === 'object' && parsedObj[key].length) {
                // Key has multiple values. Output each with that key.
                parsedObj[key].forEach(value => {
                    str += key + '=' + value + '&';
                });
            } else {
                // Key only has one value.
                str += key + '=' + parsedObj[key] + '&';
            }
        });
        return '?' + str.substring(0, str.length - 1);
    }
};

module.exports = querystring;
