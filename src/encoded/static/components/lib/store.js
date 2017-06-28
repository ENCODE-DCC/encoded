/** @preventMunge */
/* ^ see http://stackoverflow.com/questions/30110437/leading-underscore-transpiled-wrong-with-es6-classes */

import _ from 'underscore';
import { parseAndLogError } from '../globals';


export default class ItemStore {
    /*
    * Store for a collection of items persisted via the backend REST API
    *
    * items: initial collection of items
    * view: view that should be notified of changes
    * stateKey: name in the view's state that should be updated with the changed collection
    */
    constructor(items, view, stateKey) {
        this._fetch = view.context ? view.context.fetch : undefined;
        this._items = items;
        this._listeners = [{ view, stateKey }];
    }

    /* create an item */
    create(collection, data) {
        return this.fetch(collection, {
            method: 'POST',
            body: JSON.stringify(data),
        }, (response) => {
            const item = response['@graph'][0];
            this._items.push(item);
            this.dispatch('onCreate', response);
        });
    }

    /* update an item */
    update(data) {
        return this.fetch(data['@id'], {
            method: 'PUT',
            body: JSON.stringify(data),
        }, () => {
            const item = _.find(this._items, i => i['@id'] === data['@id']);
            _.extend(item, data);
            this.dispatch('onUpdate', item);
        });
    }

    /* delete an item (set its status to deleted) */
    delete(id) {
        return this.fetch(`${id}?render=false`, {
            method: 'PATCH',
            body: JSON.stringify({ status: 'deleted' }),
        }, () => {
            const item = _.find(this._items, i => i['@id'] === id);
            this._items = _.reject(this._items, i => i['@id'] === id);
            this.dispatch('onDelete', item);
        });
    }

    /* call the backend */
    fetch(url, options, then) {
        options.headers = _.extend(options.headers || {}, {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        });
        return this._fetch(
            url, options
        ).then((response) => {
            if (!response.ok) throw response;
            return response.json();
        }).then(then).catch(err =>
            parseAndLogError('ItemStore', err).then((response) => {
                this.dispatch('onError', response);
            })
        );
    }

    /* notify listening views of actions and update their state
    *  (should we update state optimistically?)
    */
    dispatch(method, arg) {
        this._listeners.forEach((listener) => {
            const view = listener.view;
            if (view[method] !== undefined) {
                view[method](arg);
            }
            const newState = {};
            newState[listener.stateKey] = this._items;
            view.setState(newState);
        });
    }
}
