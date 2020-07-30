/**
 * Manages the facet registry which directs to specific React components based on facet `field`
 * values. Unregistered fields use the default facet renderer.
 *
 * If a facet field has a value of 'assay_title' and you want to render it with the React component
 * <AssayTitleFacet>, use this to register this component for that field value:
 *
 * FacetRegistry.register('assay_title', AssayTitleFacet);
 */

class FacetRegistryCore {
    constructor() {
        this._registry = {};
        this._defaultComponent = null;
    }

    /**
     * Internal-use method to set the default facet renderer component.
     * @param {component} defaultFacet Default facet renderer
     */
    _setDefaultComponent(defaultFacet) {
        this._defaultComponent = defaultFacet;
    }

    /**
     * Register a React component to render a facet with the field value matching `field`.
     * @param {string} field facet.field value to register
     * @param {array} component Rendering component to call for this field value
     */
    register(field, component) {
        this._registry[field] = component;
    }

    /**
     * Look up the views available for the given object @type. If the given @type was never
     * registered, an array of the default types gets returned. Mostly this gets used internally
     * but available for external use if needed.
     * @param {string} resultType `type` property of search result `filters` property.
     *
     * @return {array} Array of available/registered views for the given type.
     */
    lookup(field) {
        if (this._registry[field]) {
            // Registered search result type. Sort and return saved views for that type.
            return this._registry[field];
        }

        // Return the default facet if field is unregistered, or null for null facets which
        // suppresses facet display if needed.
        return this._registry[field] === null ? null : this._defaultComponent;
    }
};


const FacetRegistry = {};
FacetRegistry.Title = new FacetRegistryCore();
FacetRegistry.Term = new FacetRegistryCore();
FacetRegistry.TermName = new FacetRegistryCore();
FacetRegistry.Facet = new FacetRegistryCore();
FacetRegistry.SelectedTermName = new FacetRegistryCore();
export default FacetRegistry;
