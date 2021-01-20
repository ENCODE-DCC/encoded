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
}


/**
 * Registry used for special facets that don't have a corresponding search-result `facet` property.
 */
class SpecialFacetRegistryCore extends FacetRegistryCore {
    /**
     * Register a React component to render a facet with the field value matching `field`.
     * `specialFieldName` exists to use as React keys, in case the registered name matches an
     * existing real facet. Returned object appears as a normal facet so existing search code can
     * work largely the same.
     * @param {string} field facet.field value to register
     * @param {array} component Rendering component to call for this field value
     * @param {string} title Title for the facet
     * @param {bool} openOnLoad True to have the facet open by default
     */
    register(field, component, title, openOnLoad) {
        const specialFieldName = `${field}-special`;
        this._registry[field] = {
            component,
            appended: false,
            field,
            specialFieldName,
            open_on_load: openOnLoad,
            title,
            special: true,
        };
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
            return this._registry[field].component;
        }

        // Return the default facet if field is unregistered, or null for null facets which
        // suppresses facet display if needed.
        return this._registry[field] === null ? null : this._defaultComponent;
    }

    getFacets() {
        return Object.keys(this._registry).map((field) => this._registry[field]);
    }
}


const FacetRegistry = {};
FacetRegistry.Title = new FacetRegistryCore();
FacetRegistry.Term = new FacetRegistryCore();
FacetRegistry.TermName = new FacetRegistryCore();
FacetRegistry.Facet = new FacetRegistryCore();
FacetRegistry.SelectedTermName = new FacetRegistryCore();
export default FacetRegistry;

export const SpecialFacetRegistry = {};
SpecialFacetRegistry.Title = new SpecialFacetRegistryCore();
SpecialFacetRegistry.Term = new SpecialFacetRegistryCore();
SpecialFacetRegistry.TermName = new SpecialFacetRegistryCore();
SpecialFacetRegistry.Facet = new SpecialFacetRegistryCore();
SpecialFacetRegistry.SelectedTermName = new SpecialFacetRegistryCore();
