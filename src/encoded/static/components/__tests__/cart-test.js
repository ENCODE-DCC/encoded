import PropTypes from 'prop-types';
import configureStore from 'redux-mock-store';
import { Provider } from 'react-redux';
import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
import Enzyme, { mount } from 'enzyme';
import _ from 'underscore';
import { cartModule, CartManager } from '../cart';
import {
    ADD_TO_CART,
    ADD_MULTIPLE_TO_CART,
    REMOVE_FROM_CART,
    REMOVE_MULTIPLE_FROM_CART,
    CACHE_SAVED_CART,
    CART_OPERATION_IN_PROGRESS,
} from '../cart/actions';
import { isAllowedElementsPossible } from '../cart/util';
import { processPseudoDefaultFiles } from '../cart/cart';

// Temporary use of adapter until Enzyme is compatible with React 17.
Enzyme.configure({ adapter: new Adapter() });

// Create the Redux mock store.
const initialCart = {
    elements: [],
    name: 'Third cart',
    current: '/carts/9570dbda-191d-42c3-8ac9-f479ca55f6f6/',
    inProgress: false,
};
const mockStore = configureStore();


describe('Cart actions', () => {
    describe('Add to cart actions', () => {
        let state;

        beforeAll(() => {
            state = {
                elements: [],
                name: 'Untitled',
                savedCartObj: {},
                inProgress: false,
            };
        });

        test('ADD_TO_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: ADD_TO_CART, elementAtId: '/experiment/ENCSR000AAA/' });
            expect(newState.elements).toHaveLength(1);
            expect(newState.elements[0]).toEqual('/experiment/ENCSR000AAA/');
            expect(newState).not.toEqual(state);
        });

        test('ADD_MULTIPLE_TO_CART works and does not mutate state', () => {
            const elementAtIds = [
                '/experiment/ENCSR000AAA/',
                '/experiment/ENCSR001AAA/',
                '/experiment/ENCSR002AAA/',
            ];
            const newState = cartModule(state, { type: ADD_MULTIPLE_TO_CART, elementAtIds });
            expect(_.isEqual(newState.elements, elementAtIds)).toEqual(true);
            expect(newState).not.toEqual(state);
        });
    });

    describe('Remove from cart actions', () => {
        let state;

        beforeAll(() => {
            state = {
                elements: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
                name: 'Untitled',
                fileViews: [],
                savedCartObj: {},
                inProgress: false,
            };
        });

        test('REMOVE_FROM_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: REMOVE_FROM_CART, elementAtId: '/experiment/ENCSR001AAA/', filePaths: [] });
            expect(newState.elements).toHaveLength(2);
            expect(newState.elements[0]).toEqual('/experiment/ENCSR000AAA/');
            expect(newState.elements[1]).toEqual('/experiment/ENCSR002AAA/');
            expect(newState).not.toEqual(state);
        });

        test('Failed REMOVE_FROM_CART does not modify contents', () => {
            const newState = cartModule(state, { type: REMOVE_FROM_CART, elementAtId: '/experiment/ENCSR004AAA/', filePaths: [] });
            expect(_.isEqual(state.elements, newState.elements)).toEqual(true);
        });

        test('REMOVE_MULTIPLE_FROM_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: REMOVE_MULTIPLE_FROM_CART, elementAtIds: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR002AAA/'] });
            expect(newState.elements).toHaveLength(1);
            expect(newState.elements[0]).toEqual('/experiment/ENCSR001AAA/');
            expect(newState).not.toEqual(state);
        });
    });

    test('CACHE_SAVED_CART works and does not mutate state', () => {
        const state = {
            elements: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
            name: 'Untitled',
            savedCartObj: {},
            inProgress: false,
        };
        const savedCartObj = {
            '@id': '/carts/eb0cf599-6a8d-44fd-8bab-227c35f0d9a8/',
            '@type': ['Cart', 'Item'],
            date_created: '2018-06-18T16:17:46.291603+00:00',
            items: ['/experiments/ENCSR001CON/', '/experiments/ENCSR002SER/', '/experiments/ENCSR003CON/'],
            name: 'J. Michael Cherry cart',
            schema_version: '1',
            status: 'current',
            submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
            uuid: 'eb0cf599-6a8d-44fd-8bab-227c35f0d9a8',
        };
        const newState = cartModule(state, { type: CACHE_SAVED_CART, savedCartObj });
        expect(_.isEqual(savedCartObj, newState.savedCartObj)).toEqual(true);
        expect(newState).not.toEqual(state);
    });

    test('CART_OPERATION_IN_PROGRESS works and does not mutate state', () => {
        let state = {
            elements: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
            name: 'Untitled',
            savedCartObj: {},
            inProgress: false,
        };
        let newState = cartModule(state, { type: CART_OPERATION_IN_PROGRESS, inProgress: true });
        expect(newState.inProgress).toEqual(true);
        expect(newState).not.toEqual(state);
        state = newState;
        newState = cartModule(state, { type: CART_OPERATION_IN_PROGRESS, inProgress: false });
        expect(newState.inProgress).toEqual(false);
        expect(newState).not.toEqual(state);
    });

    describe('Default reducer parameters', () => {
        test('Default action parameter', () => {
            const state = {
                elements: [],
                name: 'Untitled',
                savedCartObj: {},
                inProgress: false,
            };
            const newState = cartModule(state);
            expect(newState).toEqual(state);
        });

        test('Default state and action parameters', () => {
            const newState = cartModule();
            expect(newState).toBeNull();
        });
    });
});

describe('Utility functions', () => {
    test('isAllowedElementsPossible properly determines allowed types', () => {
        const filters = [
            {
                field: 'type',
                remove: '/search/?type=Experiment',
                term: 'Biosample',
            },
            {
                field: 'type',
                remove: '/search/?type=Biosample',
                term: 'Experiment',
            },
        ];
        const result = isAllowedElementsPossible(filters);
        expect(result).toBeTruthy();
    });

    test('isAllowedElementsPossible detects non-allowed types', () => {
        const filters = [
            {
                field: 'type',
                remove: '/search/?biosample_ontology.classification=whole+organisms&source.title=ATCC',
                term: 'Biosample',
            },
            {
                field: 'biosample_ontology.classification',
                remove: '/search/?type=Biosample&source.title=ATCC',
                term: 'whole organisms',
            },
            {
                field: 'source.title',
                remove: '/search/?type=Biosample&biosample_ontology.classification=whole+organisms',
                term: 'ATCC',
            },
        ];
        const result = isAllowedElementsPossible(filters);
        expect(result).toBeFalsy();
    });

    test('isAllowedElementsPossible detects no type filters', () => {
        const filters = [
            {
                field: 'searchTerm',
                remove: '/search/?biosample_ontology.term_name=A549&format=json',
                term: 'ChIP-seq',
            },
            {
                field: 'biosample_ontology.term_name',
                remove: '/search/?searchTerm=ChIP-seq&format=json',
                term: 'A549',
            },
        ];
        const result = isAllowedElementsPossible(filters);
        expect(result).toBeTruthy();
    });
});


describe('Cart manager while logged in as submitter', () => {
    let cartManager;
    let context;

    beforeAll(() => {
        context = {
            '@graph': [
                {
                    '@id': '/carts/demo-cart-for-hi-c/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    element_count: 3,
                    identifier: 'demo-cart-for-hi-c',
                    name: 'Demo cart for Hi-C',
                    status: 'current',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: 'a5307f66-4094-4db2-9747-dbf51182c34a',
                },
                {
                    '@id': '/carts/e58d40ce-615c-4822-9c44-94a4860fed22/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    date_created: '2019-02-21T22:01:54.532303+00:00',
                    element_count: 2,
                    name: 'Auto Save',
                    status: 'disabled',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: 'e58d40ce-615c-4822-9c44-94a4860fed22',
                },
                {
                    '@id': '/carts/9570dbda-191d-42c3-8ac9-f479ca55f6f6/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    date_created: '2019-02-06T21:12:42.876057+00:00',
                    element_count: 14,
                    name: 'Third cart',
                    status: 'current',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: '9570dbda-191d-42c3-8ac9-f479ca55f6f6',
                },
            ],
            '@id': '/cart-manager/',
            '@type': [
                'cart-manager',
            ],
            cart_user_max: 30,
            title: 'Cart',
        };
        const sessionProperties = {
            admin: false,
            'auth.userid': 'fytanaka@stanford.edu',
            user: {
                '@context': '/terms/',
                '@id': '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                '@type': ['User', 'Item'],
                title: 'Forrest Tanaka',
                uuid: '627eedbc-7cb3-4de3-9743-a86266e435a6',
            },
        };
        const store = mockStore(initialCart);
        cartManager = mount(
            <Provider store={store}><CartManager context={context} sessionProperties={sessionProperties} /></Provider>,
            {
                context: {
                    session_properties: sessionProperties,
                    navigate: () => { console.log('navigate'); },
                    fetch: () => { console.log('fetch'); },
                },
                childContextTypes: {
                    session_properties: PropTypes.object,
                    navigate: PropTypes.func,
                    fetch: PropTypes.func,
                },
            }
        );
    });

    test('the cart count is correct', () => {
        const tableCount = cartManager.find('.cart-counts');
        expect(tableCount.text()).toEqual('2 carts (30 maximum)');
    });

    test('the column count is correct', () => {
        const tableHeaderRows = cartManager.find('.table.table__sortable thead tr');
        expect(tableHeaderRows).toHaveLength(2);
        const tableHeaderCells = tableHeaderRows.at(1).find('th');
        expect(tableHeaderCells).toHaveLength(5);
    });

    test('the row count is correct', () => {
        const tableRows = cartManager.find('.table.table__sortable tbody tr');
        expect(tableRows).toHaveLength(3);
    });

    test('the special row CSS classes are correct', () => {
        const tableRows = cartManager.find('.table.table__sortable tbody tr');
        expect(tableRows.at(0).find('.cart-manager-table__autosave-row')).toHaveLength(1);
        expect(tableRows.at(2).find('.cart-manager-table__current-row')).toHaveLength(1);
    });
});


describe('Cart manager while logged in as admin', () => {
    let cartManager;
    let context;

    beforeAll(() => {
        context = {
            '@graph': [
                {
                    '@id': '/carts/demo-cart-for-hi-c/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    element_count: 3,
                    identifier: 'demo-cart-for-hi-c',
                    name: 'Demo cart for Hi-C',
                    status: 'current',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: 'a5307f66-4094-4db2-9747-dbf51182c34a',
                },
                {
                    '@id': '/carts/d00b9210-dcd3-4d96-9458-ec8baaef8501/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    element_count: 0,
                    name: 'My second cart',
                    status: 'deleted',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: 'd00b9210-dcd3-4d96-9458-ec8baaef8501',
                },
                {
                    '@id': '/carts/e58d40ce-615c-4822-9c44-94a4860fed22/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    date_created: '2019-02-21T22:01:54.532303+00:00',
                    element_count: 2,
                    name: 'Auto Save',
                    status: 'disabled',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: 'e58d40ce-615c-4822-9c44-94a4860fed22',
                },
                {
                    '@id': '/carts/9570dbda-191d-42c3-8ac9-f479ca55f6f6/',
                    '@type': [
                        'Cart',
                        'Item',
                    ],
                    date_created: '2019-02-06T21:12:42.876057+00:00',
                    element_count: 14,
                    name: 'Third cart',
                    status: 'current',
                    submitted_by: '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                    uuid: '9570dbda-191d-42c3-8ac9-f479ca55f6f6',
                },
            ],
            '@id': '/cart-manager/',
            '@type': [
                'cart-manager',
            ],
            cart_user_max: 30,
            title: 'Cart',
        };
        const sessionProperties = {
            admin: true,
            'auth.userid': 'fytanaka@stanford.edu',
            user: {
                '@context': '/terms/',
                '@id': '/users/627eedbc-7cb3-4de3-9743-a86266e435a6/',
                '@type': ['User', 'Item'],
                title: 'Forrest Tanaka',
                uuid: '627eedbc-7cb3-4de3-9743-a86266e435a6',
            },
        };
        const store = mockStore(initialCart);
        cartManager = mount(
            <Provider store={store}><CartManager context={context} sessionProperties={sessionProperties} /></Provider>,
            {
                context: {
                    session_properties: sessionProperties,
                    navigate: () => { console.log('navigate'); },
                    fetch: () => { console.log('fetch'); },
                },
                childContextTypes: {
                    session_properties: PropTypes.object,
                    navigate: PropTypes.func,
                    fetch: PropTypes.func,
                },
            }
        );
    });

    test('the cart count is correct', () => {
        const tableCount = cartManager.find('.cart-counts');
        expect(tableCount.text()).toEqual('2 carts (30 maximum)');
    });

    test('the column count is correct', () => {
        const tableHeaderRows = cartManager.find('.table.table__sortable thead tr');
        expect(tableHeaderRows).toHaveLength(2);
        const tableHeaderCells = tableHeaderRows.at(1).find('th');
        expect(tableHeaderCells).toHaveLength(6);
    });

    test('the row count is correct', () => {
        const tableRows = cartManager.find('.table.table__sortable tbody tr');
        expect(tableRows).toHaveLength(3);
    });

    test('the special row CSS classes are correct', () => {
        const tableRows = cartManager.find('.table.table__sortable tbody tr');
        expect(tableRows.at(0).find('.cart-manager-table__autosave-row')).toHaveLength(1);
        expect(tableRows.at(2).find('.cart-manager-table__current-row')).toHaveLength(1);
    });
});

describe('Process pseudo-default files', () => {
    let nonVisuzalizablefiles;
    let mixedBioRepFiles;
    let homogeneousOutputTypes0;
    let homogeneousOutputTypes1;

    const getDefaultFiles = (datasets) => (
        datasets.reduce((accFiles, dataset) => {
            const defaultFiles = dataset.files.filter((file) => file.preferred_default || file.pseudo_default);
            return accFiles.concat(defaultFiles);
        }, [])
    );

    beforeEach(() => {
        nonVisuzalizablefiles = [
            {
                '@id': '/files/ENCFF249UEP/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF249UEP',
                assay_term_name: 'microRNA-seq',
                assembly: 'mm10',
                biological_replicates: [1],
                file_format: 'bam',
                file_type: 'bam',
                genome_annotation: 'M21',
                output_category: 'alignment',
                output_type: 'alignments',
                status: 'released',
                technical_replicates: ['1_1'],
                title: 'ENCFF249UEP',
                uuid: 'ed01d987-3f6d-4456-b84f-95f3a55b48b9',
            },
            {
                '@id': '/files/ENCFF142RED/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF142RED',
                assay_term_name: 'microRNA-seq',
                assembly: 'mm10',
                biological_replicates: [1],
                file_format: 'tsv',
                file_type: 'tsv',
                genome_annotation: 'M21',
                output_category: 'quantification',
                output_type: 'microRNA quantifications',
                status: 'released',
                technical_replicates: ['1_1'],
                title: 'ENCFF142RED',
                uuid: '80bd2ef6-f6a0-4f6e-8079-ba8a5b3d768b',
            },
        ];

        mixedBioRepFiles = [
            {
                '@id': '/files/ENCFF650BOQ/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF650BOQ',
                assay_term_name: 'ATAC-seq',
                assembly: 'GRCh38',
                biological_replicates: [1, 2],
                file_format: 'bigWig',
                file_type: 'bigWig',
                output_category: 'signal',
                output_type: 'fold change over control',
                status: 'released',
                title: 'ENCFF650BOQ',
                uuid: '0977a1e1-cf38-4a22-ae77-bbe97a0ab93a',
            },
            {
                '@id': '/files/ENCFF565QME/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF565QME',
                assay_term_name: 'ATAC-seq',
                assembly: 'GRCh38',
                biological_replicates: [1, 2],
                file_format: 'bigWig',
                file_type: 'bigWig',
                output_category: 'signal',
                output_type: 'signal p-value',
                status: 'released',
                title: 'ENCFF565QME',
                uuid: '208d70fd-7573-4682-87e6-ace8ae048f14',
            },
        ];

        homogeneousOutputTypes0 = [
            {
                '@id': '/files/ENCFF671MSU/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF671MSU',
                assay_term_name: 'ChIP-seq',
                assembly: 'GRCh38',
                biological_replicates: [1],
                file_format: 'bigBed',
                file_format_type: 'narrowPeak',
                file_type: 'bigBed narrowPeak',
                output_category: 'annotation',
                output_type: 'pseudoreplicated peaks',
                status: 'released',
                technical_replicates: ['1_1'],
                title: 'ENCFF671MSU',
                uuid: '2636ce93-92f5-4d04-9597-a89ccc812ed6',
            },
            {
                '@id': '/files/ENCFF914XCR/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF914XCR',
                assay_term_name: 'ChIP-seq',
                assembly: 'GRCh38',
                biological_replicates: [1],
                file_format: 'bigBed',
                file_format_type: 'narrowPeak',
                file_type: 'bigBed narrowPeak',
                output_category: 'annotation',
                output_type: 'pseudoreplicated peaks',
                status: 'released',
                technical_replicates: ['2_1'],
                title: 'ENCFF914XCR',
                uuid: '011cbaee-dffc-45af-80ff-d677706e2016',
            },
        ];

        homogeneousOutputTypes1 = [
            {
                '@id': '/files/ENCFF615QOX/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF615QOX',
                assay_term_name: 'ChIP-seq',
                assembly: 'GRCh38',
                biological_replicates: [1],
                file_format: 'bigWig',
                file_type: 'bigWig',
                output_category: 'signal',
                output_type: 'fold change over control',
                status: 'released',
                technical_replicates: ['1_1'],
                title: 'ENCFF615QOX',
                uuid: '2af0c872-a65f-42d7-b5d3-7a4993123cd3',
            },
            {
                '@id': '/files/ENCFF933QRH/',
                '@type': ['File', 'Item'],
                accession: 'ENCFF933QRH',
                assay_term_name: 'ChIP-seq',
                assembly: 'GRCh38',
                biological_replicates: [2],
                file_format: 'bigWig',
                file_type: 'bigWig',
                output_category: 'signal',
                output_type: 'fold change over control',
                status: 'released',
                technical_replicates: ['2_1'],
                title: 'ENCFF933QRH',
                uuid: '4874dd69-3ce9-4fb5-bf80-a622ed7de2fd',
            },
        ];
    });

    describe('No visualizable files', () => {
        test('With no visualizable files, no preferred_default set', () => {
            const datasets = [
                {
                    '@id': '/experiments/ENCSR424VMF/',
                    '@type': ['Experiment', 'Dataset', 'Item'],
                    accession: 'ENCSR424VMF',
                    assay_slims: ['Transcription'],
                    assay_term_id: 'OBI:0001922',
                    assay_term_name: 'microRNA-seq',
                    assay_title: 'microRNA-seq',
                    assembly: ['mm10'],
                    files: nonVisuzalizablefiles,
                    perturbed: false,
                    status: 'released',
                    uuid: 'cc5c9298-168f-400d-9b61-3d56b9871d68',
                },
            ];

            processPseudoDefaultFiles(datasets);
            const preferredDefaultFiles = getDefaultFiles(datasets);
            expect(preferredDefaultFiles).toHaveLength(0);
        });
    });

    describe('Mixed biological-replicate files', () => {
        test('Mixed biological-replicate files get default, non-mixed don\'t', () => {
            const datasets = [
                {
                    '@id': '/experiments/ENCSR551CSY/',
                    '@type': ['Dataset', 'Item'],
                    accession: 'ENCSR551CSY',
                    assay_slims: ['DNA accessibility'],
                    assay_term_id: 'OBI:0002039',
                    assay_term_name: 'ATAC-seq',
                    assay_title: 'ATAC-seq',
                    assembly: ['GRCh38'],
                    files: [...nonVisuzalizablefiles, ...mixedBioRepFiles],
                    perturbed: false,
                    status: 'released',
                    uuid: 'b3d394bc-40d8-43ef-98a6-2740850e74b6',
                },
            ];

            processPseudoDefaultFiles(datasets);
            const preferredDefaultFiles = getDefaultFiles(datasets);
            expect(preferredDefaultFiles).toHaveLength(2);
        });
    });

    describe('Homogeneous output types', () => {
        test('Homogeneous output types select first bigWig/bigBed in replicate 1', () => {
            const datasets = [
                {
                    '@id': '/experiments/ENCSR587VHH/',
                    '@type': ['Experiment', 'Dataset', 'Item'],
                    accession: 'ENCSR587VHH',
                    assay_term_id: 'OBI:0000716',
                    assay_term_name: 'ChIP-seq',
                    assay_title: 'Histone ChIP-seq',
                    assembly: ['GRCh38'],
                    files: homogeneousOutputTypes0,
                    perturbed: false,
                    status: 'released',
                    uuid: 'a6385551-316f-4ec0-8604-07d4d26d97bd',
                },
            ];

            processPseudoDefaultFiles(datasets);
            const preferredDefaultFiles = getDefaultFiles(datasets);
            expect(preferredDefaultFiles).toHaveLength(1);
            expect(preferredDefaultFiles[0].accession).toEqual('ENCFF671MSU');
        });
    });

    describe('Heterogeneous output types', () => {
        test('Heterogeneous output types select first bigWig/bigBed in first replicate', () => {
            const datasets = [
                {
                    '@id': '/experiments/ENCSR587VHH/',
                    '@type': ['Experiment', 'Dataset', 'Item'],
                    accession: 'ENCSR587VHH',
                    assay_term_id: 'OBI:0000716',
                    assay_term_name: 'ChIP-seq',
                    assay_title: 'Histone ChIP-seq',
                    assembly: ['GRCh38'],
                    files: [...homogeneousOutputTypes0, ...homogeneousOutputTypes1],
                    perturbed: false,
                    status: 'released',
                    uuid: 'a6385551-316f-4ec0-8604-07d4d26d97bd',
                },
            ];

            processPseudoDefaultFiles(datasets);
            const preferredDefaultFiles = getDefaultFiles(datasets);
            expect(preferredDefaultFiles).toHaveLength(3);
            expect(preferredDefaultFiles[0].accession).toEqual('ENCFF671MSU');
            expect(preferredDefaultFiles[1].accession).toEqual('ENCFF615QOX');
            expect(preferredDefaultFiles[2].accession).toEqual('ENCFF933QRH');
        });
    });
});
