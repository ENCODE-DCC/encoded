import Gene, {
    maybeFormatStringInSquareBrackets,
    normalizeStringForMatching,
} from '../gene';


const fakeGeneItem = {
    synonyms: [
        'KAT3B',
        'RSTS2',
        'p300',
    ],
    dbxrefs: [
        'Vega:OTTHUMG00000150937',
        'ENSEMBL:ENSG00000100393',
        'HGNC:3373',
        'UniProtKB:Q09472',
        'GeneCards:EP300',
        'RefSeq:NM_001429.4',
        'UniProtKB:Q7Z6C1',
        'MIM:602700',
    ],
    locations: [
        {
            assembly: 'GRCh38',
            chromosome: 'chr22',
            start: 41092592,
            end: 41180077,
        },
        {
            assembly: 'hg19',
            chromosome: 'chr22',
            start: 41488596,
            end: 41576081,
        },
    ],
    '@id': '/genes/2033/',
    '@type': [
        'Gene',
        'Item',
    ],
    uuid: 'c77de13c-565e-4cd2-94c8-e8792e66d577',
    title: 'EP300 (Homo sapiens)',
};


describe('Gene formatting', () => {
    describe('maybeFormatStringInSquareBrackets', () => {
        test('returns empty string or string in brackets', () => {
            expect(
                maybeFormatStringInSquareBrackets('abc')
            ).toEqual('[abc]');
            expect(
                maybeFormatStringInSquareBrackets('')
            ).toEqual('');
        });
    });
    describe('normalizeStringForMatching', () => {
        test('returns lowercase string with quotes and leading/trailing whitespace removed', () => {
            expect(
                normalizeStringForMatching(
                    ' "Abc:123BBBBBBBB" '
                )
            ).toEqual('abc:123bbbbbbbb');
        });
    });
    describe('Gene object', () => {
        let gene;
        beforeEach(() => {
            gene = new Gene(
                fakeGeneItem,
                'ep300'
            );
        });
        test('getFilteredGeneSynonymsAndRefs', () => {
            expect(
                gene.getFilteredGeneSynonymsAndRefs()
            ).toEqual('[GeneCards:EP300]');
            gene = new Gene(
                fakeGeneItem,
                'UNI'
            );
            expect(
                gene.getFilteredGeneSynonymsAndRefs()
            ).toEqual(
                '[UniProtKB:Q09472, UniProtKB:Q7Z6C1]'
            );
            gene = new Gene(
                fakeGeneItem,
                'kat'
            );
            expect(
                gene.getFilteredGeneSynonymsAndRefs()
            ).toEqual(
                '[KAT3B]'
            );
        });
        test('searchTermMatchesGeneTitle', () => {
            expect(
                gene.searchTermMatchesGeneTitle()
            ).toEqual(true);
            gene = new Gene(
                fakeGeneItem,
                'UNI'
            );
            expect(
                gene.searchTermMatchesGeneTitle()
            ).toEqual(false);
        });
        test('formatGeneTitleAndMaybeSynonyms', () => {
            expect(
                gene.formatGeneTitleAndMaybeSynonyms()
            ).toEqual('EP300 (Homo sapiens)');
            gene = new Gene(
                fakeGeneItem,
                'UNI'
            );
            expect(
                gene.formatGeneTitleAndMaybeSynonyms()
            ).toEqual(
                'EP300 (Homo sapiens) [UniProtKB:Q09472, UniProtKB:Q7Z6C1]'
            );
        });
        test('asString', () => {
            expect(
                gene.asString()
            ).toEqual(
                'EP300 (Homo sapiens)'
            );
            gene = new Gene(
                fakeGeneItem,
                'kat'
            );
            expect(
                gene.asString()
            ).toEqual(
                'EP300 (Homo sapiens) [KAT3B]'
            );
        });
        test('asMatchingOrNot', () => {
            expect(
                gene.asMatchingOrNot()
            ).toEqual(
                [
                    ['match', 'EP300'],
                    ['mismatch', ' (Homo sapiens)'],
                ]
            );
            gene = new Gene(
                fakeGeneItem,
                'UNI'
            );
            expect(
                gene.asMatchingOrNot()
            ).toEqual(
                [
                    ['mismatch', 'EP300 (Homo sapiens) ['],
                    ['match', 'Uni'],
                    ['mismatch', 'ProtKB:Q09472, '],
                    ['match', 'Uni'],
                    ['mismatch', 'ProtKB:Q7Z6C1]'],
                ]
            );
        });
        test('title', () => {
            expect(
                gene.title()
            ).toEqual('EP300 (Homo sapiens)');
        });
        test('location', () => {
            expect(
                gene.location('GRCh38')
            ).toEqual(
                {
                    assembly: 'GRCh38',
                    chromosome: 'chr22',
                    start: 41092592,
                    end: 41180077,
                }
            );
        });
        test('locationForVisualization', () => {
            expect(
                gene.locationForVisualization('hg19')
            ).toEqual(
                {
                    contig: 'chr22',
                    x0: 41444853,
                    x1: 41619824,
                }
            );
        });
    });
});


export default fakeGeneItem;
