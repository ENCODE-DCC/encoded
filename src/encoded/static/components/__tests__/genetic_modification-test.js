'use strict';
/* global jest, describe, it, expect */

jest.autoMockOff();

describe('Genetic modification functionality', function() {
    const {getGMModificationTechniques} = require('../genetic_modification');

    const gmTestData = [
        {
            "uuid": "1edfd7c4-7865-4c41-86ec-6565d9dc23ca",
            "status": "released",
            "lab": "/labs/robert-waterston/",
            "award": "/awards/U41HG007355/",
            "source":"gregory-crawford",
            "modification_description": "Scientists in India have delayed the ripening of tomatoes by silencing two genes encoding N-glycoprotein modifying enzymes, α-mannosidase and β-D-N-acetylhexosaminidase.",
            "modification_genome_coordinates": {
                "assembly": "GRCh38",
                "chromosome": "11",
                "start": 20000,
                "end": 21000
            },
            "modification_purpose": "repression",
            "modification_type": "deletion",
            "modification_techniques": [
                {
                    "@type": [
                        "Tale",
                        "ModificationTechnique",
                        "Item"
                    ],
                    "aliases": [
                        "encode:tale-test-1"
                    ],
                    "uuid": "0f4bcf51-1587-402c-8550-9f6cc945b436",
                    "status": "released",
                    "lab": "/labs/robert-waterston/",
                    "award": "/awards/U41HG007355/",
                    "source": "gregory-crawford",
                    "dbxrefs": ["addgene:234235", "addgene:12345"],
                    "talen_platform":"Golden road",
                    "RVD_sequence":"NN"

                },
                {
                    "@type": [
                        "Crispr",
                        "ModificationTechnique",
                        "Item"
                    ],
                    "aliases": [
                        "encode:crispr-test-1"
                    ],
                    "uuid": "0aec2477-9507-4f9c-bf7a-b09b6b8dfd2a",
                    "status": "released",
                    "lab": "/labs/robert-waterston/",
                    "award": "/awards/U41HG007355/",
                    "dbxrefs": ["addgene:234235", "addgene:12345"],
                    "source":"gregory-crawford",
                    "insert_sequence": "CTCGGTG"
                }
            ],
            "modification_zygocity": "homozygous",
            "product_id": "CRL-2522",
            "submitted_by": "amet.fusce@est.fermentum"
        },
        {
            "uuid": "8163d8c9-15c5-4583-8b43-0e21422297a0",
            "status": "released",
            "lab": "/labs/robert-waterston/",
            "award": "/awards/U41HG007355/",
            "source":"gregory-crawford",
            "modification_type": "replacement",
            "modification_techniques": [
                {
                    "@type": [
                        "Crispr",
                        "ModificationTechnique",
                        "Item"
                    ],
                    "aliases": [
                        "encode:crispr-test-2"
                    ],
                    "uuid": "4c9733cd-7d0f-42b0-a27d-411c2b212329",
                    "status": "in progress",
                    "lab": "/labs/robert-waterston/",
                    "award": "/awards/U41HG007355/",
                    "dbxrefs": ["addgene:234235"],
                    "source":"gregory-crawford",
                    "insert_sequence": "ACTCGT"
                }
            ],
            "modification_treatments": [],
            "submitted_by": "dignissim.euismod@amet.habitant",
            "target": "/targets/H3K4me3-human"
        }
    ];

    it('it retrieves modification technique strings', function() {
        let techniques = getGMModificationTechniques(gmTestData[0]);
        expect(techniques.length).toEqual(2);
        expect(techniques[0]).toEqual('TALE');
        expect(techniques[1]).toEqual('CRISPR');

        // Try a second time to make sure we get the same results even with memoization.
        techniques = getGMModificationTechniques(gmTestData[0]);
        expect(techniques.length).toEqual(2);
        expect(techniques[0]).toEqual('TALE');
        expect(techniques[1]).toEqual('CRISPR');

        // Try a third time with a different GM to make sure memoization isn't caching results
        // improperly.
        techniques = getGMModificationTechniques(gmTestData[1]);
        expect(techniques.length).toEqual(1);
        expect(techniques[0]).toEqual('CRISPR');
    });
});
