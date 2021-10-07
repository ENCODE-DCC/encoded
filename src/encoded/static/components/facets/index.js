/**
 * Custom facet components should import and reference the global `FacetRegistry` so they can
 * connect a facet field to their rendering component. They can also import any default components
 * from defaults.js if they simply want to use or modify default functionality.
 *
 * Custom facet-renderer modules all need to be imported anonymously here so that they can register
 * themselves on page load.
 */
import FacetRegistry, { SpecialFacetRegistry } from './registry';
import { DefaultFacet, DefaultTitle, DefaultTerm, DefaultTermName, DefaultSelectedTermName } from './defaults';
import {
    FacetGroup,
    filterTopLevelFacets,
    generateFacetGroupIdentifier,
    generateFacetGroupIdentifierList,
    generateFacetGroupNameList,
    getFacetGroupFieldsInFacets,
    areFacetGroupsEqual,
} from './facet_groups';

// Custom facet-renderer modules imported here. Keep them alphabetically sorted.
import './audit';
import './biochemical_inputs';
import './date_selector';
import './exists';
import './internal_status';
import './organism';
import './perturbed';
import './status';
import './supressed';
import './type';


/**
 * Set the default facet components.
 */
FacetRegistry.Title._setDefaultComponent(DefaultTitle);
FacetRegistry.Term._setDefaultComponent(DefaultTerm);
FacetRegistry.TermName._setDefaultComponent(DefaultTermName);
FacetRegistry.Facet._setDefaultComponent(DefaultFacet);
FacetRegistry.SelectedTermName._setDefaultComponent(DefaultSelectedTermName);


/**
 * Set the default special facet components.
 */
SpecialFacetRegistry.Title._setDefaultComponent(DefaultTitle);
SpecialFacetRegistry.Term._setDefaultComponent(DefaultTerm);
SpecialFacetRegistry.TermName._setDefaultComponent(DefaultTermName);
SpecialFacetRegistry.Facet._setDefaultComponent(DefaultFacet);
SpecialFacetRegistry.SelectedTermName._setDefaultComponent(DefaultSelectedTermName);


/**
 * All usage of the facet registry external to this directory should only use what gets exported
 * here.
 */
export {
    FacetRegistry,
    SpecialFacetRegistry,
    FacetGroup,
    filterTopLevelFacets,
    generateFacetGroupIdentifier,
    generateFacetGroupIdentifierList,
    generateFacetGroupNameList,
    getFacetGroupFieldsInFacets,
    areFacetGroupsEqual,
};


/**
 * FACET REGISTRY API
 *
 * Each facet in a search-results object has a unique "field" value indicating the type of data the
 * facet contains. The facet registry lets you create custom React components to render various
 * parts of facets for a specific facet identified by its "field" value.
 *
 * You can register up to four types of components for any specific facet. The facet component
 * types are:
 *
 * Facet -- Render a complete facet, not including its title. This doesn’t have to resemble a
 * "normal" facet at all; it could include its own menus, buttons, drop-downs, etc., and can keep
 * its own React states. It receives the following properties:
 *
 *   facet - Relevant `facet` object from `facets` array in `results`.
 *
 *   results - Complete search-results object for the entire page. This can be the object for a
 *   search-results object, report object, matrix object, etc.
 *
 *   mode (optional) - Indicates any special display modes, e.g. "picker".
 *
 *   relevantFilters - Filters selected by the user corresponding to the facet given in the
 *   `facet` property.
 *
 *   pathname - Search results path without query-string portion, e.g. "/search/" or "/matrix/".
 *
 *   queryString (optional) - Query-string portion of current URL without initial question mark,
 *   e.g. "type=Experiment&status=released".
 *
 *   onFilter (optional) - Special term click handler, used for facets on edit forms.
 *
 *   allowNegation (optional) - Allow facet terms to have negation controls. Defaults to true.
 *
 *   Registration method:
 *   FacetRegistry.Facet.register(<facet field>, <React component to render this facet>);
 *
 *
 * Title -- Render the title of a facet. By default, these appear in <h5> tags, but you can do
 * anything you want here. It receives the following properties:
 *
 *   facet - Relevant `facet` object from `facets` array in `results`.
 *
 *   results - Complete search-results object for the entire page. This can be the object for a
 *   search-results object, report object, matrix object, etc.
 *
 *   mode (optional) - Indicates any special display modes, e.g. "picker".
 *
 *   pathname - Search results path without query-string portion, e.g. "/search/" or "/matrix/".
 *
 *   queryString (optional) - Query-string portion of current URL without initial question mark,
 *   e.g. "type=Experiment&status=released".
 *
 *   Registration method:
 *   FacetRegistry.Title.register(<facet field>, <React component to render this title>);
 *
 *
 * Term -- Render each term of a facet. This lets you control the display of an entire term, how
 * (and whether) it links to other searches, and any other elements of a facet term you need. The
 * component you register gets called once for each term of the facet of a specific "field" value
 * you've attached it to. If you have a custom Facet component registered, it would most likely
 * render its own terms in its own way, and you would not typically use this Term registry for that
 * case. It receives the following properties:
 *
 *   term - Relevant term object within the facet object this component has registered for.
 *
 *   facet - Relevant `facet` object from `facets` array in `results`.
 *
 *   results - Complete search-results object for the entire page. This can be the object for a
 *   search-results object, report object, matrix object, etc.
 *
 *   mode (optional) - Indicates any special display modes, e.g. "picker".
 *
 *   pathname - Search results path without query-string portion, e.g. "/search/" or "/matrix/".
 *
 *   queryString (optional)- Query-string portion of current URL without initial question mark,
 *   e.g. "type=Experiment&status=released".
 *
 *   onFilter (optional) - Special term click handler, used for facets on edit forms.
 *
 *   allowNegation (optional) - Allow facet terms to have negation controls. Defaults to true.
 *
 *   Registration method:
 *   FacetRegistry.Term.register(<facet field>, <React component to render this term>);
 *
 *
 * TermName -- Render the text within a term. This registry exists for when you want to alter the
 * styling of the text of a term without changing anything else about how the term works. The
 * component you register gets called once for each term of the facet of a specific "field" value
 * you've attached it to. If you have custom Facet or Term components registered for this facet
 * field value, they would most likely render their own term titles in their own ways, and you
 * would not typically use this TermName registry for that case. Custom TermName components receive
 * the following properties:
 *
 *   term - Relevant term object within the facet object this component has registered for. The
 *   text of the term is in `term.key` and might have the "string" or "number" type.
 *
 *   Registration method:
 *   FacetRegistry.TermName.register(<facet field>, <React component to render this term name>);
 *
 *
 * SelectedTermName -- Render the text within the "Selected filters" links. This registry exists
 * for when you need to change the styling of the terms that can be cleared from the facet, or if
 * you have a mapping of actual facet term value to displayed term within "Selected filters."
 * Custom SelectedTermName components receive the following properties:
 *
 *   filter - facets.filters object that is offered to the user for clearing. filter.term holds the
 *   name for the clear link.
 *
 *   Registration method:
 *   FacetRegistry.SelectedTermName.register(<facet field>
 *                                           <React component to render this selected term>);
 *
 *
 * Organization
 * Generally, each type of facet should be implemented in its own file and included above. However,
 * if all a custom facet does is call something in defaults.js, then that can go into a file shared
 * by all facets that only call that same default facet. For example, all facets that simply render
 * a basic "exists" facet should all share one file. If a facet calls a default facet renderer but
 * alters it in some way (e.g. the facet might appear only under certain conditions), then it might
 * be best put that custom facet and its registration into its own file.
 */
