import FacetRegistry from './registry';


/**
 * Used for all facets that need suppression unconditionally.
 */
const SuppressedFacet = () => null;

FacetRegistry.Facet.register('cart', SuppressedFacet);
