import _ from 'underscore';
import { cartModule } from '../cart';
import {
    ADD_TO_CART,
    ADD_MULTIPLE_TO_CART,
    REMOVE_FROM_CART,
    REMOVE_MULTIPLE_FROM_CART,
    CACHE_SAVED_CART,
} from '../cart/actions';
import filterAllowedItems from '../cart/util';


describe('Cart actions', () => {
    describe('Add to cart actions', () => {
        let state;

        beforeAll(() => {
            state = {
                cart: [],
                name: 'Untitled',
                savedCartObj: {},
            };
        });

        test('ADD_TO_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: ADD_TO_CART, current: '/experiment/ENCSR000AAA/' });
            expect(newState.cart).toHaveLength(1);
            expect(newState.cart[0]).toEqual('/experiment/ENCSR000AAA/');
            expect(newState).not.toEqual(state);
        });

        test('ADD_MULTIPLE_TO_CART works and does not mutate state', () => {
            const items = [
                '/experiment/ENCSR000AAA/',
                '/experiment/ENCSR001AAA/',
                '/experiment/ENCSR002AAA/',
            ];
            const newState = cartModule(state, { type: ADD_MULTIPLE_TO_CART, items });
            expect(_.isEqual(newState.cart, items)).toEqual(true);
            expect(newState).not.toEqual(state);
        });
    });

    describe('Remove from cart actions', () => {
        let state;

        beforeAll(() => {
            state = {
                cart: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
                name: 'Untitled',
                savedCartObj: {}, // Cache of saved cart
            };
        });

        test('REMOVE_FROM_CART works and does not mutate state', () => {
            const newState = cartModule(state, { type: REMOVE_FROM_CART, current: '/experiment/ENCSR001AAA/' });
            expect(newState.cart).toHaveLength(2);
            expect(newState.cart[0]).toEqual('/experiment/ENCSR000AAA/');
            expect(newState.cart[1]).toEqual('/experiment/ENCSR002AAA/');
            expect(newState).not.toEqual(state);
        });

        test('Failed REMOVE_FROM_CART does not modify contents', () => {
            const newState = cartModule(state, { type: REMOVE_FROM_CART, current: '/experiment/ENCSR004AAA/' });
            expect(_.isEqual(state.cart, newState.cart)).toEqual(true);
        });

        test('REMOVE_MULTIPLE_FROM_CART works and does not mutate state', () =>  {
            const newState = cartModule(state, { type: REMOVE_MULTIPLE_FROM_CART, items: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR002AAA/'] });
            expect(newState.cart).toHaveLength(1);
            expect(newState.cart[0]).toEqual('/experiment/ENCSR001AAA/');
            expect(newState).not.toEqual(state);
        });
    });

    test('CACHE_SAVED_CART works and does not mutate state', () => {
        const state = {
            cart: ['/experiment/ENCSR000AAA/', '/experiment/ENCSR001AAA/', '/experiment/ENCSR002AAA/'],
            name: 'Untitled',
            savedCartObj: {}, // Cache of saved cart
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
        const newState = cartModule(state, { type: CACHE_SAVED_CART, cartObj: savedCartObj });
        expect(_.isEqual(savedCartObj, newState.savedCartObj)).toEqual(true);
        expect(newState).not.toEqual(state);
    });
});


describe('Utility functions', () => {
    let items;

    beforeAll(() => {
        items = [
            { '@type': ['Experiment', 'Dataset', 'Item'], uuid: 'aca3295c-755b-4495-91cf-8a4c00a0db00' },
            { '@type': ['File', 'Item'], uuid: '46e82a90-49e5-4c33-afab-9ec90d65faf3' },
            { '@type': ['Experiment', 'Dataset', 'Item'], uuid: 'a357b33b-cdaa-4312-91c0-086bfec24181' },
            { '@type': ['PublicationData', 'FileSet', 'Dataset', 'Item'], uuid: '4eafdd35-40ea-463a-9e05-c85fb91d25d0' },
            { '@type': ['Publication', 'Item'], uuid: '52e85c70-fe2d-11e3-9191-0800200c9a66' },
        ];
    });

    test('filterAllowedItems properly filters items', () => {
        const filteredItems = filterAllowedItems(items);
        expect(filteredItems).toHaveLength(3);
        expect(filteredItems.find(item => item.uuid === 'aca3295c-755b-4495-91cf-8a4c00a0db00')).not.toBeUndefined();
        expect(filteredItems.find(item => item.uuid === 'a357b33b-cdaa-4312-91c0-086bfec24181')).not.toBeUndefined();
        expect(filteredItems.find(item => item.uuid === '4eafdd35-40ea-463a-9e05-c85fb91d25d0')).not.toBeUndefined();
        expect(filteredItems.find(item => item.uuid === '46e82a90-49e5-4c33-afab-9ec90d65faf3')).toBeUndefined();
        expect(filteredItems.find(item => item.uuid === '52e85c70-fe2d-11e3-9191-0800200c9a66')).toBeUndefined();
    });
});
