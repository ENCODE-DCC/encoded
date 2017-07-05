import 'whatwg-fetch';
import ItemStore from '../lib/store';


/* eslint no-underscore-dangle: ["error", { "allow": ["_items"] }] */

describe('ItemStore', () => {
    let items;
    let view;
    let fetch;

    beforeEach(() => {
        fetch = jest.fn();
        fetch.mockResponse = function mockResponse(data, options) {
            this.mockReturnValue(Promise.resolve(new Response(JSON.stringify(data), options || { status: 200 })));
        };
        items = [{ '@id': '/items/foo/' }];
        view = {
            context: { fetch },
            setState: jest.fn(),
        };
    });

    describe('Instantiating a store', () => {
        let store;

        beforeEach(() => {
            store = new ItemStore(items, view, 'items');
        });

        test('holds the initial items', () => {
            expect(store._items).toHaveLength(1);
        });
    });

    describe('Creating an item', () => {
        let store;
        let done;

        beforeEach(() => {
            view.onCreate = jest.fn();
            fetch.mockResponse({
                '@graph': [{ '@id': '/items/bar/' }],
            });

            store = new ItemStore(items, view, 'items');
            done = store.create('/items/', { '@id': 'bar' });
        });

        it('posts the item to the backend', () =>
            done.then(() => expect(fetch.mock.calls.length).toEqual(1))
        );

        it('updates the internal list of items', () =>
            done.then(() => expect(store._items.length).toEqual(2))
        );

        it('calls the view onCreate callback with the response', () =>
            done.then(() => {
                expect(view.onCreate).toBeCalledWith({ '@graph': [{ '@id': '/items/bar/' }] });
            })
        );

        it('notifies the view of its new state', () =>
            done.then(() => expect(view.setState.mock.calls[0][0].items.length).toEqual(2))
        );
    });

    describe('Updating an item', () => {
        let store;
        let done;

        beforeEach(() => {
            view.onUpdate = jest.fn();
            fetch.mockResponse({});

            store = new ItemStore(items, view, 'items');
            done = store.update({ '@id': '/items/foo/', updated: true });
        });

        it('puts the item to the backend', () =>
            done.then(() => {
                expect(fetch.mock.calls.length).toEqual(1);
                const args = fetch.mock.calls[0];
                expect(args[1].method).toEqual('PUT');
            })
        );

        it('updates the internal list of items', () =>
            done.then(() => expect(store._items[0].updated).toBe(true))
        );

        it('calls the view onUpdate callback with the response', () =>
            done.then(() => {
                expect(view.onUpdate).toBeCalledWith({ '@id': '/items/foo/', updated: true });
            })
        );
    });

    describe('Deleting an item', () => {
        let store;
        let done;

        beforeEach(() => {
            view.onDelete = jest.fn();
            fetch.mockResponse({});

            store = new ItemStore(items, view, 'items');
            done = store.delete('/items/foo/');
        });

        it('updates the status on the backend', () =>
            done.then(() => {
                expect(fetch.mock.calls.length).toEqual(1);
                const args = fetch.mock.calls[0];
                expect(args[1].method).toEqual('PATCH');
                const body = JSON.parse(args[1].body);
                expect(body).toEqual({ status: 'deleted' });
            })
        );

        it('updates the internal list of items', () =>
            done.then(() => expect(store._items.length).toEqual(0))
        );

        it('calls the view onDelete callback with the removed item', () =>
            done.then(() => {
                expect(view.onDelete).toBeCalledWith({ '@id': '/items/foo/' });
            })
        );
    });

    describe('Reporting errors', () => {
        it('calls the view onError callback in case of HTTP errors', () => {
            view.onError = jest.genMockFunction();
            fetch.mockResponse({ message: 'failure' }, { status: 500, headers: new Headers({ 'Content-Type': 'application/json' }) });

            const store = new ItemStore(items, view, 'items');
            return store.create('/items/', {}).then(() => {
                expect(view.onError.mock.calls[0][0].message).toEqual('failure');
            });
        });
    });
});
