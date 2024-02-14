// Implements a simple LRU cache to hold any items based on a unique key for each item.
// Based on:
// https://medium.com/dsinjs/implementing-lru-cache-in-javascript-94ba6755cda9
const CACHE_COUNT_DEFAULT = 10; // Default cache size


/**
 * Tracks one item in the double-linked-list. Not used outside the Cache class.
 */
class Node {
    constructor(key, value, next = null, prev = null) {
        this._key = key;
        this._value = value;
        this._next = next;
        this._prev = prev;
    }
}


/**
 * Implements an LRU generic cache able to hold any values identified by a unique key for each item.
 */
export default class Cache {
    /**
     * @param {number} limit Maximum number of entries in the cache
     */
    constructor(limit = CACHE_COUNT_DEFAULT) {
        this._size = 0;
        this._limit = limit;
        this._head = null;
        this._tail = null;
        this._cache = {};
    }

    /**
     * Write value to cache. This method does no collision detection, so the caller needs to make
     * sure they don't write an item with a key that already exists in the cache.
     * @param {string,number} key Unique cache-retrieval key
     * @param {any} value Value to write to the cache
     */
    write(key, value) {
        // Open space in the cache if the cache has filled.
        this._ensureLimit();

        if (!this._head) {
            // First item written to cache. Head and tail point at the new item.
            this._tail = new Node(key, value);
            this._head = this._tail;
        } else {
            // Add the new item to the cache at the head.
            const node = new Node(key, value, this._head);
            this._head._prev = node;
            this._head = node;
        }

        // Place new node in the cache index.
        this._cache[key] = this._head;
        this._size += 1;
    }

    /**
     * Read from cache and make the read node the head.
     * @param {string,number} key Identifies desired cached value
     *
     * @return {any} Cached data corresponding to key; "undefined" if cache miss
     */
    read(key) {
        if (this._cache[key]) {
            // Cache hit. Retrieve the value, then remove and rewrite the node so it moves to the
            // head for LRU and becomes most distant from being removed from the cache.
            const value = this._cache[key]._value;
            this.remove(key);
            this.write(key, value);
            return value;
        }

        // Cache miss.
        return undefined;
    }

    /**
     * Remove least-recently used node if cache bumping against its count limit.
     */
    _ensureLimit() {
        if (this._size === this._limit) {
            this.remove(this._tail._key);
        }
    }

    /**
     * Remove the node with the given key. Assumes the item exists in the cache.
     * @param {string number} key Identifies cache entry to remove
     */
    remove(key) {
        const node = this._cache[key];

        if (node._prev !== null) {
            node._prev._next = node._next;
        } else {
            this._head = node._next;
        }

        if (node._next !== null) {
            node._next._prev = node._prev;
        } else {
            this._tail = node._prev;
        }

        delete this._cache[key];
        this._size -= 1;
    }

    /**
     * Clear the cache entirely.
     */
    clear() {
        this._head = null;
        this._tail = null;
        this._size = 0;
        this._cache = {};
    }

    /**
     * Invokes the callback function with every node of the chain and the index of the node.
     * @param {func} fn Function to call with the item's node and index into the cache.
     */
    forEach(fn) {
        let node = this._head;
        let counter = 0;
        while (node) {
            fn(node, counter);
            node = node._next;
            counter += 1;
        }
    }
}
