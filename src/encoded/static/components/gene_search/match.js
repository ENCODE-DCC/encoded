import {
    MATCH,
    MISMATCH,
} from './constants';


/**
* Find all of the start indices of a pattern in a text string.
* @param {string} pattern - The pattern to search for in the string.
* @param {string} text - The string which may contain the pattern.
* @return {array} The start indices of the pattern in the text.
*/
export const getIndicesOf = (pattern, text) => {
    const indices = [];
    let currentIndex = 0;
    const patternLength = pattern.length;
    // We check patternLength to avoid infinite loop if user passes in
    // empty string. Otherwise we set the currentIndex while checking
    // the condition on every loop.
    while (
        patternLength > 0 &&
        (currentIndex = text.indexOf(pattern, currentIndex)) > -1
    ) {
        indices.push(currentIndex);
        currentIndex += patternLength;
    }
    return indices;
};


/**
* Returns array of all the start and end positions of matching patterns in a text.
* @param {string} pattern - The pattern to search for in the string.
* @param {string} text - The string which may contain the pattern.
* @return {array} Array with [start, end] positions of all the matches in a text.
*/
export const getStartAndEndPositionsForAllMatches = (pattern, text) => {
    const patternLength = pattern.length;
    return getIndicesOf(pattern, text).map(
        (index) => [index, index + patternLength]
    );
};


/**
* Returns array of matching and mismatching parts of a text. Note that
* the pattern matching can be case sensitive or insensitive.
* @param {string} pattern - The pattern to search for in the string.
* @param {string} text - The string which may contain the pattern.
* @param {boolean} caseSensitive - By default the pattern matching is case insensitive.
* @return {array} Array with partitioned text.
* >> partitionStringByMatchingOrNot(
*        'ABC',
*        'xyzABCzzzzzABC'
*    ) === [
*        ['mismatch', 'xyz'],
*        ['match', 'ABC'],
*        ['mismatch', 'zzzzz'],
*        ['match', 'ABC'],
*    ];
*/
export const partitionStringByMatchingOrNot = (pattern, text, caseSensitive = false) => {
    const partitionedText = [];
    let startIndex = 0;
    const positions = getStartAndEndPositionsForAllMatches(
        caseSensitive ? pattern : pattern.toLowerCase(),
        caseSensitive ? text : text.toLowerCase()
    );
    positions.forEach(
        ([start, end]) => {
            // Anything from the start of the string to the first match, or from the
            // end of the last match to the start of next match, is a potential mismatch.
            // If a match starts at the beginning of the string, or right at the
            // end of the last match, then `startIndex === start` and the `substring`
            // method just returns an empty string that is filtered out later.
            partitionedText.push(
                [
                    MISMATCH,
                    text.substring(startIndex, start),
                ]
            );
            // The part from start to end position is actual match.
            partitionedText.push(
                [
                    MATCH,
                    text.substring(start, end),
                ]
            );
            // For the next round we set the potential mismatch to start
            // at the end of the current match.
            startIndex = end;
        }
    );
    // If the rest of the string is a mismatch.
    if (startIndex < text.length) {
        partitionedText.push(
            [
                MISMATCH,
                text.substring(startIndex),
            ]
        );
    }
    // Only return substrings that exist.
    return partitionedText.filter(
        ([, value]) => Boolean(value)
    );
};
