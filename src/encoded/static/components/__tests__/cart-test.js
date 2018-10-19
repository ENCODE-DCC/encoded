import _ from 'underscore';
import { cartModule } from '../cart';
import {
    ADD_TO_CART,
    ADD_MULTIPLE_TO_CART,
    REMOVE_FROM_CART,
    REMOVE_MULTIPLE_FROM_CART,
    CACHE_SAVED_CART,
    CART_OPERATION_IN_PROGRESS,
} from '../cart/actions';
import { isAllowedElementsPossible } from '../cart/util';


describe('Cart actions', () => {
    describe('Add to cart actions', () => {
        let state;

        beforeAll(() => {
            state = {
                cart: [],
                name: 'Untitled',
                savedCartObj: {},
                inProgress: false,
            };
        });

        test('ADD_TO_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: ADD_TO_CART, elementAtId: '/experiment/ENCSR000AAA/' });
            expect(newState.cart).toHaveLength(1);
            expect(newState.cart[0]).toEqual('/experiment/ENCSR000AAA/');
            expect(newState).not.toEqual(state);
        });

        test('ADD_MULTIPLE_TO_CART works and does not mutate state', () => {
            const elementAtIds = [
                '/experiment/ENCSR000AAA/',
                '/experiment/ENCSR001AAA/',
                '/experiment/ENCSR002AAA/',
            ];
            const newState = cartModule(state, { type: ADD_MULTIPLE_TO_CART, elementAtIds });
            expect(_.isEqual(newState.cart, elementAtIds)).toEqual(true);
            expect(newState).not.toEqual(state);
        });
    });

    describe('Remove from cart actions', () => {
        let state;

        beforeAll(() => {
            state = {
                cart: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
                name: 'Untitled',
                savedCartObj: {},
                inProgress: false,
            };
        });

        test('REMOVE_FROM_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: REMOVE_FROM_CART, elementAtId: '/experiment/ENCSR001AAA/' });
            expect(newState.cart).toHaveLength(2);
            expect(newState.cart[0]).toEqual('/experiment/ENCSR000AAA/');
            expect(newState.cart[1]).toEqual('/experiment/ENCSR002AAA/');
            expect(newState).not.toEqual(state);
        });

        test('Failed REMOVE_FROM_CART does not modify contents', () => {
            const newState = cartModule(state, { type: REMOVE_FROM_CART, elementAtId: '/experiment/ENCSR004AAA/' });
            expect(_.isEqual(state.cart, newState.cart)).toEqual(true);
        });

        test('REMOVE_MULTIPLE_FROM_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: REMOVE_MULTIPLE_FROM_CART, elementAtIds: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR002AAA/'] });
            expect(newState.cart).toHaveLength(1);
            expect(newState.cart[0]).toEqual('/experiment/ENCSR001AAA/');
            expect(newState).not.toEqual(state);
        });
    });

    test('CACHE_SAVED_CART works and does not mutate state', () => {
        const state = {
            cart: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
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
            cart: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
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
                cart: [],
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
                remove: '/search/?biosample_type=whole+organisms&source.title=ATCC',
                term: 'Biosample',
            },
            {
                field: 'biosample_type',
                remove: '/search/?type=Biosample&source.title=ATCC',
                term: 'whole organisms',
            },
            {
                field: 'source.title',
                remove: '/search/?type=Biosample&biosample_type=whole+organisms',
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
                remove: '/search/?biosample_term_name=A549&format=json',
                term: 'ChIP-seq',
            },
            {
                field: 'biosample_term_name',
                remove: '/search/?searchTerm=ChIP-seq&format=json',
                term: 'A549',
            },
        ];
        const result = isAllowedElementsPossible(filters);
        expect(result).toBeTruthy();
    });
});
