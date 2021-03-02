import {
    getIndicesOf,
    getStartAndEndPositionsForAllMatches,
    partitionStringByMatchingOrNot,
} from '../match';


describe('Pattern match', () => {
    describe('getIndicesOf', () => {
        test('find indices of all matches to user input', () => {
            expect(
                getIndicesOf(
                    'abc',
                    '1234abcdefg'
                )
            ).toEqual([4]);
            expect(
                getIndicesOf(
                    'abc',
                    '1234abcdefgabc'
                )
            ).toEqual([4, 11]);
            expect(
                getIndicesOf(
                    'abc',
                    '1234abcdefgabcabexyzasdf'
                )
            ).toEqual([4, 11]);
            expect(
                getIndicesOf(
                    'abc',
                    'abcabcabcabcabcabcabcabc'
                )
            ).toEqual([0, 3, 6, 9, 12, 15, 18, 21]);
            expect(
                getIndicesOf(
                    'abc',
                    '234asdfckdbcak4wz sdf cxv '
                )
            ).toEqual([]);
            expect(
                getIndicesOf(
                    'ABC'.toLowerCase(),
                    'ABCxyz'
                )
            ).toEqual([]);
            expect(
                getIndicesOf(
                    'ABC'.toLowerCase(),
                    'ABCxyz'.toLowerCase()
                )
            ).toEqual([0]);
            expect(
                getIndicesOf(
                    '',
                    'ABCxyz'
                )
            ).toEqual([]);
            expect(
                getIndicesOf(
                    'abc',
                    ''
                )
            ).toEqual([]);
            expect(
                getIndicesOf(
                    '',
                    ''
                )
            ).toEqual([]);
        });
    });
    describe('getStartAndEndPositionForAllMatches', () => {
        test('returns list of start and end positions for matching patterns in text', () => {
            expect(
                getStartAndEndPositionsForAllMatches(
                    'abc',
                    '1234abcdefg'
                )
            ).toEqual(
                [
                    [4, 7],
                ],
            );
            expect(
                getStartAndEndPositionsForAllMatches(
                    'abc',
                    '1234abcdefgabcabexyzasdf'
                )
            ).toEqual(
                [
                    [4, 7],
                    [11, 14],
                ],
            );
            expect(
                getStartAndEndPositionsForAllMatches(
                    'abc',
                    'abcabcabcabcabcabcabcabc'
                )
            ).toEqual(
                [
                    [0, 3],
                    [3, 6],
                    [6, 9],
                    [9, 12],
                    [12, 15],
                    [15, 18],
                    [18, 21],
                    [21, 24],
                ]
            );
            expect(
                getStartAndEndPositionsForAllMatches(
                    'ABC'.toLowerCase(),
                    'ABCxyz'
                )
            ).toEqual([]);
        });
    });
    describe('partitionStringByMatchingOrNot', () => {
        test('partitions string by whether it matches pattern or not', () => {
            expect(
                partitionStringByMatchingOrNot(
                    'abc',
                    'abcdef'
                )
            ).toEqual(
                [
                    ['match', 'abc'],
                    ['mismatch', 'def'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    'ABC',
                    'xyzABCzzzzzABC'
                )
            ).toEqual(
                [
                    ['mismatch', 'xyz'],
                    ['match', 'ABC'],
                    ['mismatch', 'zzzzz'],
                    ['match', 'ABC'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    'ABC',
                    'xyzABCzzzzzABC',
                    true
                )
            ).toEqual(
                [
                    ['mismatch', 'xyz'],
                    ['match', 'ABC'],
                    ['mismatch', 'zzzzz'],
                    ['match', 'ABC'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    'abc',
                    'xyzABCzzzzzABC'
                )
            ).toEqual(
                [
                    ['mismatch', 'xyz'],
                    ['match', 'ABC'],
                    ['mismatch', 'zzzzz'],
                    ['match', 'ABC'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    'abc',
                    'xyzABCzzzzzabc',
                    true
                )
            ).toEqual(
                [
                    ['mismatch', 'xyzABCzzzzz'],
                    ['match', 'abc'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    'abc',
                    'abcabcabcabcabcabcabcabc'
                )
            ).toEqual(
                [
                    ['match', 'abc'],
                    ['match', 'abc'],
                    ['match', 'abc'],
                    ['match', 'abc'],
                    ['match', 'abc'],
                    ['match', 'abc'],
                    ['match', 'abc'],
                    ['match', 'abc'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    '',
                    'abcabcabcabcabcabcabcabc'
                )
            ).toEqual(
                [
                    ['mismatch', 'abcabcabcabcabcabcabcabc'],
                ]
            );
            expect(
                partitionStringByMatchingOrNot(
                    'tr',
                    'Dontraaa and treb'
                )
            ).toEqual(
                [
                    ['mismatch', 'Don'],
                    ['match', 'tr'],
                    ['mismatch', 'aaa and '],
                    ['match', 'tr'],
                    ['mismatch', 'eb'],
                ]
            );
        });
    });
});
