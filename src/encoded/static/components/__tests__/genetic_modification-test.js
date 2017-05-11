import { getGMTechniques, calcGMSummarySentence } from '../genetic_modification';


describe('Genetic modification functionality', () => {
    const gmTestData = [
        {
            uuid: '1edfd7c4-7865-4c41-86ec-6565d9dc23ca',
            status: 'released',
            lab: '/labs/robert-waterston/',
            award: '/awards/U41HG007355/',
            source: 'gregory-crawford',
            description: 'Scientists in India have delayed the ripening of tomatoes by silencing two genes encoding N-glycoprotein modifying enzymes, α-mannosidase and β-D-N-acetylhexosaminidase.',
            modified_site: {
                assembly: 'GRCh38',
                chromosome: '11',
                start: 20000,
                end: 21000,
            },
            purpose: 'repression',
            modification_type: 'deletion',
            modification_techniques: [
                {
                    '@type': [
                        'Tale',
                        'ModificationTechnique',
                        'Item',
                    ],
                    aliases: [
                        'encode:tale-test-1',
                    ],
                    uuid: '0f4bcf51-1587-402c-8550-9f6cc945b436',
                    status: 'released',
                    lab: '/labs/robert-waterston/',
                    award: '/awards/U41HG007355/',
                    source: 'gregory-crawford',
                    dbxrefs: ['addgene:234235', 'addgene:12345'],
                    talen_platform: 'Golden road',
                    RVD_sequence: 'NN',

                },
                {
                    '@type': [
                        'Crispr',
                        'ModificationTechnique',
                        'Item',
                    ],
                    aliases: [
                        'encode:crispr-test-1',
                    ],
                    uuid: '0aec2477-9507-4f9c-bf7a-b09b6b8dfd2a',
                    status: 'released',
                    lab: '/labs/robert-waterston/',
                    award: '/awards/U41HG007355/',
                    dbxrefs: ['addgene:234235', 'addgene:12345'],
                    source: 'gregory-crawford',
                    insert_sequence: 'CTCGGTG',
                },
            ],
            zygosity: 'homozygous',
            product_id: 'CRL-2522',
            submitted_by: 'amet.fusce@est.fermentum',
        },
        {
            uuid: '8163d8c9-15c5-4583-8b43-0e21422297a0',
            status: 'released',
            lab: '/labs/robert-waterston/',
            award: '/awards/U41HG007355/',
            source: 'gregory-crawford',
            modification_type: 'replacement',
            modification_techniques: [
                {
                    '@type': [
                        'Crispr',
                        'ModificationTechnique',
                        'Item',
                    ],
                    aliases: [
                        'encode:crispr-test-2',
                    ],
                    uuid: '4c9733cd-7d0f-42b0-a27d-411c2b212329',
                    status: 'in progress',
                    lab: '/labs/robert-waterston/',
                    award: '/awards/U41HG007355/',
                    dbxrefs: ['addgene:234235'],
                    source: 'gregory-crawford',
                    insert_sequence: 'ACTCGT',
                }
            ],
            treatments: [
                require('../testdata/treatment/CHEBI34730'),
                require('../testdata/treatment/CHEBI44616')
            ],
            submitted_by: 'dignissim.euismod@amet.habitant',
            target: require('../testdata/target/HNRNPA1-human')
        }
    ];

    test('retrieves modification technique strings', () => {
        let techniques = getGMTechniques(gmTestData[0]);
        expect(techniques.length).toEqual(2);
        expect(techniques[0]).toEqual('CRISPR');
        expect(techniques[1]).toEqual('TALE');

        // Try a second time to make sure we get the same results even with memoization.
        techniques = getGMTechniques(gmTestData[0]);
        expect(techniques.length).toEqual(2);
        expect(techniques[0]).toEqual('CRISPR');
        expect(techniques[1]).toEqual('TALE');

        // Try a third time with a different GM to make sure memoization isn't caching results
        // improperly.
        techniques = getGMTechniques(gmTestData[1]);
        expect(techniques.length).toEqual(1);
        expect(techniques[0]).toEqual('CRISPR');
    });

    test('calculates summary sentences', () => {
        const summary = calcGMSummarySentence(gmTestData[1]);
        expect(summary).toEqual('replacement of HNRNPA1 using CRISPR, 97.2 nM doxycycline hyclate (CHEBI:34730) for 6 hour, 600 nM afimoxifene (CHEBI:44616) for 30 minute');
    });
});
