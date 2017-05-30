import Registry from '../registry';

const testObj = { '@type': ['Test', 'Item'] };
const specificObj = { '@type': ['Specific', 'Item'] };
const otherObj = { '@type': ['Other'] };

const views = [
    { for_: 'Item' },
    { for_: 'Specific' },
    { name: 'named', for_: 'Item' },
];

/* eslint no-underscore-dangle: ["error", { "allow": ["for_"] }]*/
function makeOne() {
    const registry = new Registry();
    views.forEach((view) => {
        registry.register(view, view.for_, view.name);
    });
    registry.fallback = () => ({ fallback: true });
    return registry;
}

describe('The registry library', () => {
    it('is able to lookup views for item in order of specificity', () => {
        const registry = makeOne();
        expect(registry.lookup(testObj).for_).toBe('Item');
        expect(registry.lookup(specificObj).for_).toBe('Specific');
    });

    it('is able to lookup named views for item', () => {
        const registry = makeOne();
        expect(registry.lookup(testObj, 'named').name).toBe('named');
    });

    it('is able to fallback to view for objects with unknown types', () => {
        const registry = makeOne();
        expect(registry.lookup(otherObj).fallback).toBe(true);
    });
});
